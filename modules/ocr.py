from __future__ import annotations
import re
import os
import sys
from typing import List, Tuple, Optional
from datetime import datetime
from pathlib import Path

from PIL import Image

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None

# Regex general para códigos (2-5 letras + 3-9 dígitos)
CODE_REGEX = re.compile(r"^[A-Z]{2,5}\d{3,9}$")

# Prefijos válidos específicos para mejorar precisión del OCR
VALID_PREFIXES = (
    'CQ', 'CGF', 'CHW', 'TY', 'CAT', 'BAT', 'GF', 'BST', 'ST', 
    'CST', 'PF', 'CPF', 'KC', 'CKC', 'HW', 'QC', 'TL', 'CTL'
)

# Patrones de corrección común para errores de OCR
OCR_CORRECTIONS = {
    # Letras confundidas con números
    'O': '0', 'I': '1', 'L': '1', 'S': '5', 'Z': '2', 'B': '8',
    # Números confundidos con letras (en la parte de letras)
    '0': 'O', '1': 'I', '5': 'S', '2': 'Z', '8': 'B',
}

# =============================================================================
# INICIALIZACIÓN LAZY DE EASYOCR
# =============================================================================

_reader = None


def _get_reader():
    """
    Obtiene o crea la instancia singleton del lector EasyOCR.
    Inicialización lazy para evitar retraso al importar el módulo.
    """
    global _reader
    if _reader is None:
        import easyocr
        # gpu=False para compatibilidad universal
        # verbose=False para evitar mensajes en consola
        _reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _reader


# =============================================================================
# PREPROCESAMIENTO DE IMÁGENES
# =============================================================================

def _resize_if_needed(img: np.ndarray, max_dimension: int = 2000) -> np.ndarray:
    """
    Redimensiona la imagen si es demasiado grande para mejorar rendimiento.
    Mantiene la proporción.
    """
    h, w = img.shape[:2]
    if max(h, w) <= max_dimension:
        return img
    
    scale = max_dimension / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _enhance_contrast(gray: np.ndarray) -> np.ndarray:
    """Mejora el contraste usando CLAHE."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _binarize_otsu(gray: np.ndarray) -> np.ndarray:
    """Binarización usando método Otsu."""
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def _binarize_adaptive(gray: np.ndarray) -> np.ndarray:
    """Binarización adaptativa para imágenes con iluminación variable."""
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )


def _preprocess_standard(im: Image.Image) -> np.ndarray:
    """
    Preprocesamiento estándar:
    1. Redimensionar si es muy grande
    2. Escala de grises
    3. CLAHE para contraste
    4. Binarización Otsu
    """
    if cv2 is None or np is None:
        return np.array(im)

    arr = np.array(im)
    arr = _resize_if_needed(arr)

    # Escala de grises
    if len(arr.shape) == 3:
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    else:
        gray = arr

    enhanced = _enhance_contrast(gray)
    binary = _binarize_otsu(enhanced)
    return binary


def _preprocess_aggressive(im: Image.Image) -> np.ndarray:
    """
    Preprocesamiento más agresivo para imágenes difíciles:
    1. Redimensionar
    2. Escala de grises
    3. Denoise
    4. CLAHE
    5. Binarización adaptativa
    """
    if cv2 is None or np is None:
        return np.array(im)

    arr = np.array(im)
    arr = _resize_if_needed(arr)

    if len(arr.shape) == 3:
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    else:
        gray = arr

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    enhanced = _enhance_contrast(denoised)
    binary = _binarize_adaptive(enhanced)
    return binary


def _is_annotated_bbox(img: np.ndarray, bbox_coords: Tuple[int, int, int, int]) -> bool:
    """
    Detecta si un código tiene anotaciones (líneas/tachados) alrededor.
    Busca líneas horizontales cerca del texto que indiquen que fue marcado.
    """
    if cv2 is None or np is None:
        return False

    x0, y0, x1, y1 = bbox_coords
    w = x1 - x0
    h = y1 - y0
    
    if w <= 0 or h <= 0:
        return False
    
    pad = max(1, int(h * 0.3))

    ry0 = max(0, y0 - pad)
    ry1 = min(img.shape[0], y1 + pad)
    rx0 = max(0, x0)
    rx1 = min(img.shape[1], x1)

    roi = img[ry0:ry1, rx0:rx1]
    if roi.size == 0:
        return False

    # Convertir a gris si es necesario
    if len(roi.shape) == 3:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    else:
        gray = roi

    # Detectar bordes
    edges = cv2.Canny(gray, 50, 150)
    
    # Buscar líneas horizontales
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, w // 6), 1))
    lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # Sumar píxeles por fila para detectar líneas horizontales fuertes
    horizontal = np.sum(lines, axis=1)
    if len(horizontal) == 0:
        return False
    
    # Si hay una fila con muchos píxeles blancos, hay una línea
    threshold = 255 * max(1, (w // 10))
    return np.max(horizontal) > threshold


# =============================================================================
# FUNCIÓN PRINCIPAL DE EXTRACCIÓN
# =============================================================================

def _try_fix_code(text: str) -> Optional[str]:
    """
    Intenta corregir errores comunes de OCR en el código.
    Retorna el código corregido o None si no es válido.
    """
    txt = text.strip().upper()
    if not txt or len(txt) < 5:
        return None
    
    # Primero verificar si ya es válido con un prefijo conocido
    for prefix in VALID_PREFIXES:
        if txt.startswith(prefix):
            rest = txt[len(prefix):]
            if rest.isdigit() and 3 <= len(rest) <= 9:
                return txt
    
    # Si el formato general es correcto, aceptar
    if CODE_REGEX.match(txt):
        return txt
    
    # Intentar corregir errores de OCR
    # Separar parte de letras y números
    letter_part = ''
    number_part = ''
    in_numbers = False
    
    for char in txt:
        if char.isdigit():
            in_numbers = True
            number_part += char
        elif char.isalpha():
            if in_numbers:
                # Letra después de números - probablemente error OCR
                # Intentar convertir a número
                if char in OCR_CORRECTIONS:
                    number_part += OCR_CORRECTIONS[char]
                else:
                    number_part += char  # Mantener para validación posterior
            else:
                letter_part += char
        else:
            # Número en la parte de letras
            if not in_numbers and char in '01258':
                conv = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B'}
                letter_part += conv.get(char, char)
            else:
                number_part += char
    
    # Verificar si el prefijo corregido es válido
    for prefix in VALID_PREFIXES:
        if letter_part == prefix:
            if number_part.isdigit() and 3 <= len(number_part) <= 9:
                return letter_part + number_part
    
    # Intentar con el formato general
    if 2 <= len(letter_part) <= 5 and letter_part.isalpha():
        if number_part.isdigit() and 3 <= len(number_part) <= 9:
            return letter_part + number_part
    
    return None


def _extract_codes_from_text(text: str) -> List[str]:
    """
    Extrae códigos de un texto usando patrones específicos.
    """
    codes = []
    
    # Patrón para prefijos conocidos seguidos de números
    prefix_pattern = '|'.join(VALID_PREFIXES)
    pattern = re.compile(rf'({prefix_pattern})\s*(\d{{3,9}})', re.IGNORECASE)
    
    for match in pattern.finditer(text.upper()):
        prefix = match.group(1).upper()
        numbers = match.group(2)
        code = prefix + numbers
        if code not in codes:
            codes.append(code)
    
    # También buscar códigos con formato general
    general_pattern = re.compile(r'\b([A-Z]{2,5})(\d{3,9})\b')
    for match in general_pattern.finditer(text.upper()):
        code = match.group(1) + match.group(2)
        if code not in codes and CODE_REGEX.match(code):
            codes.append(code)
    
    return codes


def extract_codes_from_image(
    image_path: Path, min_confidence: int = 40
) -> List[Tuple[str, bool, Optional[datetime]]]:
    """
    Extrae códigos de una imagen usando EasyOCR.
    
    Realiza múltiples pasadas con diferentes configuraciones para
    maximizar la detección de códigos.
    
    Prefijos soportados: CQ, CGF, CHW, TY, CAT, BAT, GF, BST, ST, 
                         CST, PF, CPF, KC, CKC, HW, QC, TL, CTL

    Args:
        image_path: Ruta a la imagen
        min_confidence: Confianza mínima para aceptar un resultado (0-100)

    Returns:
        Lista de tuplas (codigo, anotado, fecha)
    """
    reader = _get_reader()
    im = Image.open(str(image_path))
    
    # Convertir a RGB si tiene canal alpha
    if im.mode == 'RGBA':
        im = im.convert('RGB')
    elif im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')

    # Imagen original en formato cv2 para detección de anotaciones
    if cv2 is not None and np is not None:
        cv_img = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    else:
        cv_img = None

    allowlist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    confidence_threshold = min_confidence / 100.0
    
    found_codes: set = set()
    items: List[Tuple[str, bool, Optional[datetime]]] = []
    all_raw_texts: List[Tuple[str, list, float]] = []  # (text, bbox, conf)
    
    # Configuraciones de OCR a probar (en orden)
    ocr_attempts = [
        # Pasada 1: Imagen preprocesada estándar
        {'image': _preprocess_standard(im), 'name': 'standard'},
        # Pasada 2: Imagen original (a veces funciona mejor)
        {'image': np.array(im) if np is not None else str(image_path), 'name': 'original'},
        # Pasada 3: Preprocesamiento agresivo
        {'image': _preprocess_aggressive(im), 'name': 'aggressive'},
    ]
    
    for attempt in ocr_attempts:
        try:
            results = reader.readtext(
                attempt['image'],
                allowlist=allowlist,
                detail=1,
                paragraph=False,
                min_size=8,
                text_threshold=0.5,
                low_text=0.25,
                width_ths=0.7,
                decoder='greedy',
            )
        except Exception:
            continue
        
        for bbox, text, conf in results:
            txt = text.strip().upper()
            if not txt:
                continue
            
            all_raw_texts.append((txt, bbox, conf))
            
            # Intentar extraer códigos del texto detectado
            # A veces OCR detecta múltiples códigos en un solo resultado
            extracted = _extract_codes_from_text(txt)
            for code in extracted:
                if code not in found_codes:
                    found_codes.add(code)
                    annotated = False
                    if cv_img is not None:
                        try:
                            xs = [int(p[0]) for p in bbox]
                            ys = [int(p[1]) for p in bbox]
                            bbox_coords = (min(xs), min(ys), max(xs), max(ys))
                            annotated = _is_annotated_bbox(cv_img, bbox_coords)
                        except Exception:
                            pass
                    items.append((code, annotated, datetime.utcnow()))
            
            # También intentar corrección directa
            if conf >= confidence_threshold:
                fixed = _try_fix_code(txt)
                if fixed and fixed not in found_codes:
                    found_codes.add(fixed)
                    annotated = False
                    if cv_img is not None:
                        try:
                            xs = [int(p[0]) for p in bbox]
                            ys = [int(p[1]) for p in bbox]
                            bbox_coords = (min(xs), min(ys), max(xs), max(ys))
                            annotated = _is_annotated_bbox(cv_img, bbox_coords)
                        except Exception:
                            pass
                    items.append((fixed, annotated, datetime.utcnow()))
        
        # Si ya encontramos suficientes códigos, no necesitamos más pasadas
        if len(items) >= 3:
            break
    
    # Si no encontramos nada, intentar una última vez concatenando textos cercanos
    if not items and all_raw_texts:
        # Ordenar por posición Y y luego X
        sorted_texts = sorted(all_raw_texts, key=lambda x: (int(x[1][0][1]), int(x[1][0][0])))
        combined_text = ' '.join([t[0] for t in sorted_texts])
        extracted = _extract_codes_from_text(combined_text)
        for code in extracted:
            if code not in found_codes:
                found_codes.add(code)
                items.append((code, False, datetime.utcnow()))
    
    return items
