from __future__ import annotations

import logging
from pathlib import Path

import requests

from src.config import config

logger = logging.getLogger(__name__)


def post_to_facebook(message: str, image_path: Path | None = None) -> None:
    if not config.fb_page_access_token or not config.fb_page_id:
        raise RuntimeError("FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID must be set in .env")

    base = f"https://graph.facebook.com/v20.0/{config.fb_page_id}"
    if image_path:
        files = {"source": open(image_path, "rb")}
        data = {"caption": message, "access_token": config.fb_page_access_token}
        resp = requests.post(f"{base}/photos", files=files, data=data, timeout=60)
    else:
        data = {"message": message, "access_token": config.fb_page_access_token}
        resp = requests.post(f"{base}/feed", data=data, timeout=60)

    if not resp.ok:
        logger.error("Facebook post failed: %s", resp.text)
        resp.raise_for_status()
