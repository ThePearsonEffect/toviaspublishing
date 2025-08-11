from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

import requests

from src.config import config


def _wp_auth_header() -> dict[str, str]:
    token = base64.b64encode(f"{config.wp_username}:{config.wp_application_password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def post_to_wordpress(title: str, content: str, featured_image_path: Optional[Path] = None) -> int:
    if not (config.wp_base_url and config.wp_username and config.wp_application_password):
        raise RuntimeError("WordPress credentials missing in .env")

    media_id: Optional[int] = None
    if featured_image_path:
        with open(featured_image_path, "rb") as f:
            media_resp = requests.post(
                f"{config.wp_base_url}/wp-json/wp/v2/media",
                headers={**_wp_auth_header(), "Content-Disposition": f"attachment; filename={featured_image_path.name}"},
                files={"file": (featured_image_path.name, f, "image/png")},
                timeout=60,
            )
        media_resp.raise_for_status()
        media_id = media_resp.json().get("id")

    post = {"title": title, "content": content, "status": "publish"}
    if media_id:
        post["featured_media"] = media_id

    resp = requests.post(f"{config.wp_base_url}/wp-json/wp/v2/posts", headers=_wp_auth_header(), json=post, timeout=60)
    resp.raise_for_status()
    return resp.json().get("id")
