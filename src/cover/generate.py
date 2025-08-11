from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class CoverTemplate:
    width: int = 1800
    height: int = 2700
    background_color: tuple[int, int, int] = (20, 20, 24)
    accent_color: tuple[int, int, int] = (255, 215, 0)
    title_color: tuple[int, int, int] = (255, 255, 255)
    author_color: tuple[int, int, int] = (200, 200, 200)
    quote_color: tuple[int, int, int] = (230, 230, 230)
    title_font_path: Optional[str] = None
    author_font_path: Optional[str] = None
    quote_font_path: Optional[str] = None


@dataclass
class TShirtTemplate:
    width: int = 4500
    height: int = 5400
    text_color: tuple[int, int, int, int] = (255, 255, 255, 255)
    stroke_color: tuple[int, int, int, int] = (0, 0, 0, 255)
    title_font_path: Optional[str] = None
    quote_font_path: Optional[str] = None


def _load_font(path: Optional[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size=size)
    except Exception:
        pass
    return ImageFont.load_default()


def _wrap_text(text: str, draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont, max_width: int) -> str:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        test = " ".join(current + [word])
        w, _ = draw.textsize(test, font=font)
        if w <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def generate_cover(title: str, author: str, quote: str, out_path: Path, template: CoverTemplate | None = None) -> Path:
    template = template or CoverTemplate()
    canvas = Image.new("RGB", (template.width, template.height), template.background_color)
    draw = ImageDraw.Draw(canvas)

    title_font = _load_font(template.title_font_path, 120)
    author_font = _load_font(template.author_font_path, 64)
    quote_font = _load_font(template.quote_font_path, 48)

    cv_img = np.array(canvas)
    cv_img = cv2.circle(cv_img, (template.width // 2, template.height // 3), template.width // 2,
                        tuple(int(c * 0.5) for c in template.accent_color), thickness=4)
    cv_img = cv2.GaussianBlur(cv_img, (0, 0), sigmaX=7)
    canvas = Image.fromarray(cv_img)
    draw = ImageDraw.Draw(canvas)

    title_wrapped = _wrap_text(title, draw, title_font, int(template.width * 0.8))
    w, h = draw.multiline_textsize(title_wrapped, font=title_font, spacing=10)
    draw.multiline_text(((template.width - w) // 2, int(template.height * 0.12)), title_wrapped,
                        fill=template.title_color, font=title_font, align="center", spacing=10)

    author_text = author
    w_a, h_a = draw.textsize(author_text, font=author_font)
    draw.text(((template.width - w_a) // 2, int(template.height * 0.28) + h), author_text,
              fill=template.author_color, font=author_font)

    quote_width = int(template.width * 0.75)
    quote_wrapped = _wrap_text(f"“{quote}”", draw, quote_font, quote_width)
    w_q, h_q = draw.multiline_textsize(quote_wrapped, font=quote_font, spacing=6)
    draw.multiline_text(((template.width - w_q) // 2, int(template.height * 0.5)), quote_wrapped,
                        fill=template.quote_color, font=quote_font, align="center", spacing=6)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path


def generate_tshirt_design(text: str, out_path: Path, title: Optional[str] = None, template: TShirtTemplate | None = None) -> Path:
    template = template or TShirtTemplate()
    canvas = Image.new("RGBA", (template.width, template.height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    title_font = _load_font(template.title_font_path, 220)
    quote_font = _load_font(template.quote_font_path, 180)

    center_x = template.width // 2
    max_width = int(template.width * 0.8)

    y = int(template.height * 0.2)
    if title:
        title_wrapped = _wrap_text(title, draw, title_font, max_width)
        w_t, h_t = draw.multiline_textsize(title_wrapped, font=title_font, spacing=12)
        draw.multiline_text((center_x - w_t // 2, y), title_wrapped,
                            font=title_font, fill=template.text_color, spacing=12,
                            align="center", stroke_width=6, stroke_fill=template.stroke_color)
        y += h_t + 80

    quote_wrapped = _wrap_text(text, draw, quote_font, max_width)
    w_q, h_q = draw.multiline_textsize(quote_wrapped, font=quote_font, spacing=10)
    draw.multiline_text((center_x - w_q // 2, y), quote_wrapped,
                        font=quote_font, fill=template.text_color, spacing=10,
                        align="center", stroke_width=6, stroke_fill=template.stroke_color)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path
