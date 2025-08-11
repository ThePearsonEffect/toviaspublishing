from __future__ import annotations

import logging
from pathlib import Path

import requests

from src.config import config

logger = logging.getLogger(__name__)


def post_to_instagram(message: str, image_path: Path) -> None:
    if not (config.ig_access_token and config.ig_business_account_id):
        raise RuntimeError("IG_ACCESS_TOKEN and IG_BUSINESS_ACCOUNT_ID must be set in .env")

    # Instagram Graph API requires a publicly accessible image URL (no direct file upload).
    # Upload your image to WordPress or another host first, then use that URL here.
    raise NotImplementedError("Provide a public image URL and implement IG Graph API media + publish flow.")
