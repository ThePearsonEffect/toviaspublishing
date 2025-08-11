from __future__ import annotations

from pathlib import Path
from typing import List

from PIL import Image, ImageDraw, ImageFont
import random


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        test = " ".join(cur + [w])
        w_px, _ = draw.textsize(test, font=font)
        if w_px <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return "\n".join(lines)


def create_quote_tile(quote: str, author: str, out_path: Path, size: int = 1080) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg_colors = [(18, 18, 22), (24, 28, 32), (10, 30, 60), (60, 20, 20)]
    fg_colors = [(240, 240, 240), (230, 230, 230), (255, 255, 255)]
    accent = (255, 215, 0)

    img = Image.new("RGB", (size, size), random.choice(bg_colors))
    draw = ImageDraw.Draw(img)

    quote_font = _load_font(48)
    author_font = _load_font(32)

    margin = int(size * 0.08)
    max_w = size - margin * 2

    wrapped = _wrap(draw, f"“{quote}”", quote_font, max_w)
    w, h = draw.multiline_textsize(wrapped, font=quote_font, spacing=8)
    x = (size - w) // 2
    y = (size - h) // 2 - 40

    draw.multiline_text((x+2, y+2), wrapped, font=quote_font, fill=(0,0,0), spacing=8)
    draw.multiline_text((x, y), wrapped, font=quote_font, fill=random.choice(fg_colors), spacing=8, align="center")

    author_text = f"— {author}" if author else ""
    w_a, h_a = draw.textsize(author_text, font=author_font)
    draw.text(((size - w_a)//2, y + h + 20), author_text, font=author_font, fill=accent)

    img.save(out_path)
    return out_path


def generate_quote_tiles(quotes: List[str], author: str, out_dir: Path, prefix: str = "quote") -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    for idx, q in enumerate(quotes, start=1):
        p = out_dir / f"{prefix}_{idx:02d}.png"
        create_quote_tile(q, author, p)
        paths.append(p)
    return paths


def compose_message(book_title: str, author: str, quote: str, hashtags: list[str] | None = None) -> str:
    base_tags = [
        f"#{book_title.strip().replace(' ', '')}",
        f"#{author.strip().split()[-1] if author else 'author'}",
        "#books", "#reading", "#booklover",
    ]
    if hashtags:
        base_tags.extend(hashtags)
    unique_tags = []
    seen = set()
    for t in base_tags:
        if t.lower() not in seen:
            unique_tags.append(t)
            seen.add(t.lower())
    return f"{quote}\n\n— {author}\n\n" + " ".join(unique_tags)
