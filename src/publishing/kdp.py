from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright

from src.config import config


async def _login_kdp(page) -> None:
    await page.goto("https://kdp.amazon.com/")
    await page.click("text=Sign in")
    await page.fill("#ap_email", config.kdp_email or "")
    await page.fill("#ap_password", config.kdp_password or "")
    await page.click("#signInSubmit")
    await page.wait_for_load_state("networkidle")


async def upload_book_to_kdp(ebook_path: Optional[Path], paperback_pdf_path: Optional[Path], title: str) -> None:
    if not config.kdp_email or not config.kdp_password:
        raise RuntimeError("KDP_EMAIL and KDP_PASSWORD must be set in .env")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await _login_kdp(page)

        # Placeholders; update selectors as the UI may change.
        await page.click("text=Create")
        if ebook_path:
            await page.click("text=Kindle eBook")
            # TODO: Fill details and upload .epub
        if paperback_pdf_path:
            await page.click("text=Paperback")
            # TODO: Fill details and upload .pdf

        await page.wait_for_timeout(30000)
        await browser.close()


def upload_sync(ebook_path: Optional[Path], paperback_pdf_path: Optional[Path], title: str) -> None:
    asyncio.run(upload_book_to_kdp(ebook_path, paperback_pdf_path, title))
