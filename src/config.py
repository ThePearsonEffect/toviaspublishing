from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class AppConfig:
    environment: str = os.getenv("ENV", "development")
    output_dir: str = os.getenv("OUTPUT_DIR", "output")

    tesseract_cmd: str | None = os.getenv("TESSERACT_CMD")

    grammarly_client_id: str | None = os.getenv("GRAMMARLY_CLIENT_ID")
    grammar_provider: str = os.getenv("GRAMMAR_PROVIDER", "languagetool")
    languagetool_api_url: str = os.getenv("LANGUAGETOOL_API_URL", "https://api.languagetool.org/v2")

    kdp_email: str | None = os.getenv("KDP_EMAIL")
    kdp_password: str | None = os.getenv("KDP_PASSWORD")

    fb_page_access_token: str | None = os.getenv("FB_PAGE_ACCESS_TOKEN")
    fb_page_id: str | None = os.getenv("FB_PAGE_ID")

    ig_access_token: str | None = os.getenv("IG_ACCESS_TOKEN")
    ig_business_account_id: str | None = os.getenv("IG_BUSINESS_ACCOUNT_ID")

    wp_base_url: str | None = os.getenv("WP_BASE_URL")
    wp_username: str | None = os.getenv("WP_USERNAME")
    wp_application_password: str | None = os.getenv("WP_APPLICATION_PASSWORD")


config = AppConfig()


def ensure_output_dir() -> str:
    os.makedirs(config.output_dir, exist_ok=True)
    return config.output_dir
