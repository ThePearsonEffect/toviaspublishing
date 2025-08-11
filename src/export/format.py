from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from EbookLib import epub


def export_to_pdf(text_file: Path, out_pdf: Path) -> Path:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_pdf), pagesize=LETTER)
    width, height = LETTER
    margin = 72
    y = height - margin

    with open(text_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if y < margin:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line)
            y -= 14
    c.save()
    return out_pdf


def export_to_epub(text_file: Path, out_epub: Path, title: str = "Book", author: str = "Author") -> Path:
    out_epub.parent.mkdir(parents=True, exist_ok=True)
    book = epub.EpubBook()
    book.set_identifier("id123456")
    book.set_title(title)
    book.set_language("en")
    book.add_author(author)

    with open(text_file, "r", encoding="utf-8") as f:
        content = f.read()

    chapter = epub.EpubHtml(title="Chapter 1", file_name="chap_01.xhtml", lang="en")
    chapter.content = f"<h1>{title}</h1><pre>{content}</pre>"

    book.add_item(chapter)
    book.toc = (epub.Link("chap_01.xhtml", "Chapter 1", "chap_01"),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", chapter]

    epub.write_epub(str(out_epub), book)
    return out_epub
