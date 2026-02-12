import re
from typing import List, Tuple, Optional
from datetime import datetime
from pathlib import Path

from PIL import Image
import pytesseract

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None

CODE_REGEX = re.compile(r"^[A-Z]{2,5}\d{3,9}$")

def _preprocess_for_ocr(im: Image.Image) -> Image.Image:
    if cv2 is None or np is None:
        return im
    arr = np.array(im)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)
    _, th = cv2.threshold(eq, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    scale = 1.5
    th = cv2.resize(th, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    return Image.fromarray(th)

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

def extract_codes_from_image(image_path: Path) -> List[Tuple[str, bool, Optional[datetime]]]:
    im = Image.open(str(image_path))
    pim = _preprocess_for_ocr(im)
    data = pytesseract.image_to_data(pim, output_type=pytesseract.Output.DICT)
    items: List[Tuple[str, bool, Optional[datetime]]] = []
    if cv2 is not None and np is not None:
        cv_img = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    else:
        cv_img = None
    n = len(data["text"])
    for i in range(n):
        txt = data["text"][i].strip().upper()
        if not txt or not CODE_REGEX.match(txt):
            continue
        x = int(data["left"][i])
        y = int(data["top"][i])
        w = int(data["width"][i])
        h = int(data["height"][i])
        annotated = False
        if cv_img is not None:
            annotated = _is_annotated_bbox(cv_img, (x, y, w, h))
        items.append((txt, annotated, datetime.utcnow()))
    return items
