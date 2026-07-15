from __future__ import annotations

import json
from typing import cast

import pytest

from backend import handler


class FakeContext:
    def __init__(self, aws_request_id: str = "req-123") -> None:
        self.aws_request_id = aws_request_id


def build_event(
    body: object = '{"question": "¿Qué es AWS Lambda?"}',
    method: str = "POST",
    *,
    is_base64_encoded: bool = False,
) -> dict[str, object]:
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/",
        "requestContext": {
            "http": {
                "method": method,
            }
        },
        "isBase64Encoded": is_base64_encoded,
        "body": body,
    }


def decode_body(response: dict[str, object]) -> dict[str, object]:
    body = response["body"]
    assert isinstance(body, str)
    parsed_body = json.loads(body)
    assert isinstance(parsed_body, dict)
    return cast(dict[str, object], parsed_body)


def decode_error(response: dict[str, object]) -> dict[str, str]:
    decoded = decode_body(response)["error"]
    assert isinstance(decoded, dict)
    return cast(dict[str, str], decoded)


def test_lambda_handler_returns_fixed_answer_for_valid_post_request() -> None:
    response = handler.lambda_handler(
        build_event(body='{"question": "  ¿Qué es AWS Lambda?  "}'),
        FakeContext(),
    )

    assert response["statusCode"] == 200
    assert response["headers"] == {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        "Content-Type": "application/json",
    }
    decoded = decode_body(response)
    assert "answer" in decoded
    assert "¿Qué es AWS Lambda?" in str(decoded["answer"])


def test_lambda_handler_accepts_dictionary_bodies_for_local_tests() -> None:
    response = handler.lambda_handler(
        build_event(body={"question": "Pregunta local"}),
        FakeContext(),
    )

    assert response["statusCode"] == 200
    assert "Pregunta local" in str(decode_body(response)["answer"])


def test_lambda_handler_rejects_invalid_json() -> None:
    response = handler.lambda_handler(
        build_event(body='{"question": invalid json}'),
        FakeContext(),
    )

    assert response["statusCode"] == 400
    assert decode_body(response) == {
        "error": {
            "code": "INVALID_JSON",
            "message": "El cuerpo debe ser JSON válido.",
        }
    }


@pytest.mark.parametrize(
    "body",
    [
        "{}",
        '{"question": ""}',
        '{"question": "   "}',
        '{"question": 123}',
        None,
    ],
)
def test_lambda_handler_rejects_missing_or_invalid_question(body: object) -> None:
    response = handler.lambda_handler(build_event(body=body), FakeContext())

    assert response["statusCode"] == 400
    assert decode_error(response)["code"] == "INVALID_REQUEST"


def test_lambda_handler_rejects_too_long_question() -> None:
    response = handler.lambda_handler(
        build_event(body=json.dumps({"question": "a" * 1001})),
        FakeContext(),
    )

    assert response["statusCode"] == 400
    assert decode_error(response)["code"] == "QUESTION_TOO_LONG"


def test_lambda_handler_rejects_wrong_method() -> None:
    response = handler.lambda_handler(build_event(method="GET"), FakeContext())

    assert response["statusCode"] == 405
    assert decode_body(response) == {
        "error": {
            "code": "METHOD_NOT_ALLOWED",
            "message": "Solo se admite el método POST.",
        }
    }


def test_lambda_handler_rejects_base64_request_body() -> None:
    response = handler.lambda_handler(
        build_event(body="eyJxdWVzdGlvbiI6ICJob2xhIn0=", is_base64_encoded=True),
        FakeContext(),
    )

    assert response["statusCode"] == 400
    assert decode_error(response)["code"] == "INVALID_REQUEST"


def test_lambda_handler_returns_internal_error_without_leaking_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def crash(_: str) -> str:
        raise RuntimeError("boom-internal-details")

    monkeypatch.setattr(handler, "build_fixed_answer", crash)

    response = handler.lambda_handler(build_event(), FakeContext())

    assert response["statusCode"] == 500
    decoded = decode_body(response)
    assert decoded == {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Ha ocurrido un error interno inesperado.",
        }
    }
    assert "boom-internal-details" not in json.dumps(decoded)


def test_lambda_handler_treats_missing_method_as_post_for_local_compatibility() -> None:
    event = build_event()
    event.pop("requestContext")
    response = handler.lambda_handler(event, FakeContext())

    assert response["statusCode"] == 200
