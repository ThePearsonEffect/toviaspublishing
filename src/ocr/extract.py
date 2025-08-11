from __future__ import annotations

import re
import hashlib
from pathlib import Path
from typing import Iterable, List

import cv2
import numpy as np
import pytesseract

from src.config import config
from src.utils.cache import memoize


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _prepare_image_for_ocr(image_path: Path) -> np.ndarray:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 11)
    return thresh


def _ocr_image_cached(image_path: Path) -> str:
    file_hash = _hash_file(image_path)
    key = f"ocr:{file_hash}"

    def run() -> str:
        processed = _prepare_image_for_ocr(image_path)
        return pytesseract.image_to_string(processed, lang="eng")

    if config.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd

    return memoize(key, run)


def extract_text_from_images(image_paths: Iterable[Path]) -> str:
    texts: List[str] = []
    for path in image_paths:
        text = _ocr_image_cached(path)
        texts.append(text)
    return "\n\n".join(texts)


def extract_quotes(text: str) -> List[str]:
    pattern = r"\“([^\”]+)\”|\"([^\"]+)\"|\'([^\']+)\'"
    quotes: List[str] = []
    for match in re.finditer(pattern, text):
        for group in match.groups():
            if group:
                cleaned = group.strip()
                if len(cleaned.split()) >= 3:
                    quotes.append(cleaned)
    if not quotes:
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip().split()) > 5]
        quotes = paragraphs[:5]
    return quotes
