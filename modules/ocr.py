from __future__ import annotations
import re
import os
from typing import List, Tuple, Optional
from datetime import datetime
from pathlib import Path

from PIL import Image
import pytesseract

# Configuración de Tesseract portable
_MODULE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
TESSERACT_DIR = _MODULE_DIR / "tesseract"
TESSERACT_PATH = TESSERACT_DIR / "tesseract.exe"
TESSDATA_PATH = TESSERACT_DIR / "tessdata"

# Configurar ejecutable de Tesseract
pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)

# Configuración óptima para documentos con ruido
# --tessdata-dir: Ruta DIRECTA a la carpeta tessdata
# --oem 3: Usa LSTM + Legacy (mejor precisión)
# --psm 6: Asume un bloque uniforme de texto
# -l eng: Diccionario inglés
# tessedit_char_whitelist: Solo caracteres esperados en códigos
TESSERACT_CONFIG = f'--tessdata-dir "{TESSDATA_PATH}" --oem 3 --psm 6 -l eng -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# Configuración alternativa para imágenes muy ruidosas
TESSERACT_CONFIG_LEGACY = f'--tessdata-dir "{TESSDATA_PATH}" --oem 0 --psm 11 -l eng -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None

CODE_REGEX = re.compile(r"^[A-Z]{2,5}\d{3,9}$")

# =============================================================================
# PIPELINE DE PREPROCESAMIENTO OPTIMIZADO
# =============================================================================

def _calculate_optimal_scale(img: np.ndarray, target_height: int = 300) -> float:
    """
    Calcula el factor de escala óptimo para que el texto tenga ~300px de altura.
    Tesseract funciona mejor con texto de 30-40px de altura mínima.
    """
    h = img.shape[0]
    if h < 100:
        return 3.0  # Imágenes muy pequeñas
    elif h < 200:
        return 2.0
    elif h < target_height:
        return target_height / h
    return 1.0


def _upscale_image(img: np.ndarray, scale: float = None) -> np.ndarray:
    """
    Escala la imagen usando INTER_CUBIC para preservar calidad.
    INTER_CUBIC es mejor que INTER_LINEAR para upscaling de texto.
    """
    if scale is None:
        scale = _calculate_optimal_scale(img)
    
    if scale <= 1.0:
        return img
    
    # INTER_CUBIC: Mejor para agrandar, preserva bordes
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


def _convert_to_grayscale(img: np.ndarray) -> np.ndarray:
    """Convierte a escala de grises si es necesario."""
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def _apply_bilateral_filter(gray: np.ndarray) -> np.ndarray:
    """
    Filtro bilateral: Reduce ruido PRESERVANDO bordes.
    - d=9: Diámetro del vecindario
    - sigmaColor=75: Filtro en espacio de color
    - sigmaSpace=75: Filtro en espacio de coordenadas
    """
    return cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)


def _apply_adaptive_threshold(gray: np.ndarray) -> np.ndarray:
    """
    Umbral adaptativo Gaussiano - mejor para iluminación no uniforme.
    """
    return cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2
    )


def _apply_otsu_threshold(gray: np.ndarray) -> np.ndarray:
    """
    Otsu's Thresholding: Encuentra el umbral óptimo automáticamente.
    Ideal para imágenes con histograma bimodal (texto negro sobre fondo claro).
    """
    # Aplicar blur gaussiano ligero antes de Otsu para reducir ruido
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def _detect_skew_angle(binary: np.ndarray) -> float:
    """
    Detecta el ángulo de inclinación del texto usando proyección horizontal.
    Retorna el ángulo en grados.
    """
    # Encontrar coordenadas de píxeles blancos (texto)
    coords = np.column_stack(np.where(binary > 0))
    
    if len(coords) < 100:
        return 0.0
    
    # Calcular el ángulo usando minAreaRect
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    
    # Normalizar ángulo
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90
    
    # Solo corregir si la inclinación es significativa pero no extrema
    if abs(angle) < 0.5 or abs(angle) > 15:
        return 0.0
    
    return angle


def _deskew_image(img: np.ndarray, angle: float) -> np.ndarray:
    """
    Corrige la inclinación de la imagen rotando por el ángulo detectado.
    """
    if abs(angle) < 0.5:
        return img
    
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    
    # Matriz de rotación
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Calcular nuevo tamaño para no recortar
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    
    # Ajustar la matriz de transformación
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    
    # Aplicar rotación con fondo blanco
    rotated = cv2.warpAffine(
        img, M, (new_w, new_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255) if len(img.shape) == 3 else 255
    )
    
    return rotated


def _remove_noise_morphology(binary: np.ndarray) -> np.ndarray:
    """
    Limpieza morfológica para eliminar ruido pequeño.
    """
    # Kernel para operaciones morfológicas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    
    # Opening: Elimina ruido pequeño (erosión + dilatación)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Closing: Cierra pequeños huecos en el texto
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    return cleaned


def _add_border(img: np.ndarray, border_size: int = 10) -> np.ndarray:
    """
    Añade borde blanco alrededor de la imagen.
    Tesseract funciona mejor con margen alrededor del texto.
    """
    return cv2.copyMakeBorder(
        img, border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT,
        value=255
    )


def _preprocess_for_ocr(im: Image.Image, aggressive: bool = False) -> Image.Image:
    """
    Pipeline completo de preprocesamiento optimizado para OCR.
    
    Pasos:
    1. Escalado dinámico (INTER_CUBIC)
    2. Conversión a escala de grises
    3. Filtro bilateral (preserva bordes, reduce ruido)
    4. Otsu's Thresholding (binarización automática)
    5. Detección y corrección de inclinación (Deskewing)
    6. Limpieza morfológica
    7. Añadir borde
    
    Args:
        im: Imagen PIL de entrada
        aggressive: Si True, aplica preprocesamiento más agresivo para imágenes muy ruidosas
    
    Returns:
        Imagen PIL preprocesada
    """
    if cv2 is None or np is None:
        return im
    
    # Convertir PIL a numpy array
    arr = np.array(im)
    
    # Asegurar formato BGR si es color
    if len(arr.shape) == 3 and arr.shape[2] == 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    
    # 1. Escalado dinámico
    arr = _upscale_image(arr)
    
    # 2. Escala de grises
    gray = _convert_to_grayscale(arr)
    
    # 3. Filtro bilateral (preserva bordes)
    filtered = _apply_bilateral_filter(gray)
    
    # 4. CLAHE para mejorar contraste local
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(filtered)
    
    # 5. Binarización con Otsu
    if aggressive:
        # Para imágenes muy ruidosas, usar umbral adaptativo
        binary = _apply_adaptive_threshold(enhanced)
    else:
        binary = _apply_otsu_threshold(enhanced)
    
    # 6. Detección y corrección de inclinación
    angle = _detect_skew_angle(binary)
    if abs(angle) > 0.5:
        binary = _deskew_image(binary, angle)
    
    # 7. Limpieza morfológica
    cleaned = _remove_noise_morphology(binary)
    
    # 8. Añadir borde
    final = _add_border(cleaned, border_size=15)
    
    return Image.fromarray(final)

def _is_annotated_bbox(img, bbox) -> bool:
    if cv2 is None or np is None:
        return False
    x, y, w, h = bbox
    pad = max(1, int(h * 0.2))
    x0 = max(0, x)
    y0 = max(0, y - pad)
    x1 = min(img.shape[1] - 1, x + w)
    y1 = min(img.shape[0] - 1, y + h + pad)
    roi = img[y0:y1, x0:x1]
    if roi.size == 0:
        return False
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, w // 8), 1))
    lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    horizontal = np.sum(lines, axis=1)
    if len(horizontal) == 0:
        return False
    if np.max(horizontal) > 255 * max(1, (w // 12)):
        return True
    return False

def extract_codes_from_image(image_path: Path, min_confidence: int = 60) -> List[Tuple[str, bool, Optional[datetime]]]:
    """
    Extrae códigos de una imagen usando OCR optimizado.
    
    Args:
        image_path: Ruta a la imagen
        min_confidence: Confianza mínima para aceptar un resultado (0-100)
    
    Returns:
        Lista de tuplas (codigo, anotado, fecha)
    """
    im = Image.open(str(image_path))
    
    # Preprocesamiento estándar
    pim = _preprocess_for_ocr(im, aggressive=False)
    
    # Primera pasada con configuración estándar (OEM 3 + PSM 6)
    data = pytesseract.image_to_data(
        pim, 
        config=TESSERACT_CONFIG,
        output_type=pytesseract.Output.DICT
    )
    
    items: List[Tuple[str, bool, Optional[datetime]]] = []
    found_codes = set()  # Para evitar duplicados
    
    if cv2 is not None and np is not None:
        cv_img = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    else:
        cv_img = None
    
    n = len(data["text"])
    for i in range(n):
        txt = data["text"][i].strip().upper()
        conf = int(data["conf"][i]) if data["conf"][i] != '-1' else 0
        
        # Filtrar por confianza y regex
        if not txt or conf < min_confidence or not CODE_REGEX.match(txt):
            continue
        
        # Evitar duplicados
        if txt in found_codes:
            continue
        found_codes.add(txt)
        
        x = int(data["left"][i])
        y = int(data["top"][i])
        w = int(data["width"][i])
        h = int(data["height"][i])
        
        annotated = False
        if cv_img is not None:
            annotated = _is_annotated_bbox(cv_img, (x, y, w, h))
        
        items.append((txt, annotated, datetime.utcnow()))
    
    # Si no se encontraron resultados, intentar con configuración alternativa (más agresiva)
    if not items:
        pim_aggressive = _preprocess_for_ocr(im, aggressive=True)
        data = pytesseract.image_to_data(
            pim_aggressive,
            config=TESSERACT_CONFIG_LEGACY,
            output_type=pytesseract.Output.DICT
        )
        
        n = len(data["text"])
        for i in range(n):
            txt = data["text"][i].strip().upper()
            conf = int(data["conf"][i]) if data["conf"][i] != '-1' else 0
            
            if not txt or conf < (min_confidence - 20) or not CODE_REGEX.match(txt):
                continue
            
            if txt in found_codes:
                continue
            found_codes.add(txt)
            
            x = int(data["left"][i])
            y = int(data["top"][i])
            w = int(data["width"][i])
            h = int(data["height"][i])
            
            annotated = False
            if cv_img is not None:
                annotated = _is_annotated_bbox(cv_img, (x, y, w, h))
            
            items.append((txt, annotated, datetime.utcnow()))
    
    return items


def get_ocr_confidence(image_path: Path) -> dict:
    """
    Función de diagnóstico para ver la confianza de cada detección.
    Útil para debugging y ajuste de parámetros.
    """
    im = Image.open(str(image_path))
    pim = _preprocess_for_ocr(im)
    
    data = pytesseract.image_to_data(
        pim,
        config=TESSERACT_CONFIG,
        output_type=pytesseract.Output.DICT
    )
    
    results = []
    for i in range(len(data["text"])):
        txt = data["text"][i].strip()
        if txt:
            results.append({
                "text": txt,
                "confidence": data["conf"][i],
                "matches_regex": bool(CODE_REGEX.match(txt.upper()))
            })
    
    return {
        "total_detections": len(results),
        "detections": results
    }
