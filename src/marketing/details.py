from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ProductDetails:
    title: str
    description: str
    tags: List[str]


def _join_tags(tags: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for t in tags:
        key = t.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(t.strip())
    return result


def generate_book_cover_details(book_title: str, author: str, quote: str) -> ProductDetails:
    title = f"{book_title} — Quote Cover"
    desc_lines = [
        f"From {author}:",
        f"\n“{quote}”\n",
        "High-resolution cover artwork suitable for posts and promotions.",
        "Designed automatically with balanced typography and contrast.",
    ]
    tags = _join_tags([
        "books", "reading", "booklover", "quote", "literature",
        book_title.replace(" ", ""), author.split()[-1] if author else "author",
    ])
    return ProductDetails(title=title, description="\n".join(desc_lines), tags=tags)


def generate_tshirt_details(book_title: str, author: str, text: str) -> ProductDetails:
    title = f"{book_title} — Quote Tee"
    desc_lines = [
        f"Typography tee inspired by {book_title} by {author}.",
        f"Front print: “{text}”",
        "Print-ready transparent PNG at 4500x5400 px.",
        "Great for POD platforms or personal merchandise.",
    ]
    tags = _join_tags([
        "tshirt", "apparel", "quote", "reader", "bookish",
        book_title.replace(" ", ""), author.split()[-1] if author else "author",
    ])
    return ProductDetails(title=title, description="\n".join(desc_lines), tags=tags)
