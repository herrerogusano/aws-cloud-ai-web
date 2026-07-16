from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/check_backend_endpoint.py <function-url>")

    url = sys.argv[1]
    request = Request(url, method="GET")

    try:
        with urlopen(request, timeout=10) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8")
    except URLError as exc:  # pragma: no cover - exercised by workflow failures
        raise RuntimeError(f"Network error while requesting {url}: {exc.reason}") from exc

    if status != 405:
        raise RuntimeError(f"Unexpected status {status} from backend endpoint {url}")

    payload = json.loads(body)
    error = payload.get("error")

    if not isinstance(error, dict):
        raise RuntimeError("Backend smoke check response is missing an error object")

    if error.get("code") != "METHOD_NOT_ALLOWED":
        raise RuntimeError(
            f"Backend smoke check returned the wrong error code: {error.get('code')!r}"
        )

    print(f"Backend endpoint smoke check passed for {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
