"""Response helpers for the local Lambda handler."""

from __future__ import annotations

import json
from collections.abc import Mapping

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
}


def json_response(
    status_code: int,
    payload: Mapping[str, object],
    headers: Mapping[str, str] | None = None,
) -> dict[str, object]:
    response_headers = dict(DEFAULT_HEADERS)
    if headers is not None:
        response_headers.update(headers)

    return {
        "statusCode": status_code,
        "headers": response_headers,
        "body": json.dumps(payload, ensure_ascii=False),
    }


def error_response(status_code: int, code: str, message: str) -> dict[str, object]:
    return json_response(
        status_code=status_code,
        payload={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )
