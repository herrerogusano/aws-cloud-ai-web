from __future__ import annotations

import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import urlopen

EXPECTED_TITLE = "<title>Pregunta a la IA</title>"
EXPECTED_ASSET_PATHS = ["styles.css", "app.js", "config.js"]


def fetch_text(url: str) -> tuple[int, str]:
    try:
        with urlopen(url, timeout=10) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            return status, body
    except HTTPError as exc:  # pragma: no cover - exercised by workflow failures
        raise RuntimeError(f"HTTP error while requesting {url}: {exc.code}") from exc
    except URLError as exc:  # pragma: no cover - exercised by workflow failures
        raise RuntimeError(f"Network error while requesting {url}: {exc.reason}") from exc


def assert_contains(haystack: str, needle: str, description: str) -> None:
    if needle not in haystack:
        raise RuntimeError(f"Missing {description}: expected to find {needle!r}")


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/check_frontend_website.py <website-url>")

    website_url = sys.argv[1].rstrip("/")
    homepage_status, homepage_body = fetch_text(website_url)

    if homepage_status != 200:
        raise RuntimeError(f"Unexpected homepage status {homepage_status} for {website_url}")

    assert_contains(homepage_body, EXPECTED_TITLE, "page title")

    for asset_path in EXPECTED_ASSET_PATHS:
        asset_url = urljoin(f"{website_url}/", asset_path)
        asset_status, _ = fetch_text(asset_url)
        if asset_status != 200:
            raise RuntimeError(f"Unexpected asset status {asset_status} for {asset_url}")

    print(f"Frontend website smoke check passed for {website_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
