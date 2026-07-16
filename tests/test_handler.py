from __future__ import annotations

import json
from typing import cast

import pytest

from backend import bedrock_client, handler


class FakeContext:
    def __init__(self, aws_request_id: str = "req-123") -> None:
        self.aws_request_id = aws_request_id


def build_event(
    body: object = '{"question": "Que es AWS Lambda?"}',
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


def patch_bedrock_success(monkeypatch: pytest.MonkeyPatch, answer: str = "Respuesta real") -> None:
    settings = bedrock_client.BedrockSettings(
        model_id="eu.amazon.nova-micro-v1:0",
        max_tokens=500,
        temperature=0.3,
    )
    monkeypatch.setattr(handler, "load_bedrock_settings", lambda: settings)
    monkeypatch.setattr(handler, "generate_answer", lambda question, *, settings: answer)


def test_lambda_handler_returns_bedrock_answer_for_valid_post_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_bedrock_success(monkeypatch, answer="AWS Lambda ejecuta codigo sin servidores.")

    response = handler.lambda_handler(
        build_event(body='{"question": "  Que es AWS Lambda?  "}'),
        FakeContext(),
    )

    assert response["statusCode"] == 200
    assert response["headers"] == {"Content-Type": "application/json"}
    decoded = decode_body(response)
    assert decoded == {"answer": "AWS Lambda ejecuta codigo sin servidores."}


def test_lambda_handler_accepts_dictionary_bodies_for_local_tests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_bedrock_success(monkeypatch, answer="Respuesta local")

    response = handler.lambda_handler(
        build_event(body={"question": "Pregunta local"}),
        FakeContext(),
    )

    assert response["statusCode"] == 200
    assert decode_body(response)["answer"] == "Respuesta local"


def test_lambda_handler_rejects_invalid_json() -> None:
    response = handler.lambda_handler(
        build_event(body='{"question": invalid json}'),
        FakeContext(),
    )

    assert response["statusCode"] == 400
    assert decode_body(response) == {
        "error": {
            "code": "INVALID_JSON",
            "message": "El cuerpo debe ser JSON valido.",
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
            "message": "Solo se admite el metodo POST.",
        }
    }


def test_lambda_handler_rejects_base64_request_body() -> None:
    response = handler.lambda_handler(
        build_event(body="eyJxdWVzdGlvbiI6ICJob2xhIn0=", is_base64_encoded=True),
        FakeContext(),
    )

    assert response["statusCode"] == 400
    assert decode_error(response)["code"] == "INVALID_REQUEST"


def test_lambda_handler_returns_controlled_llm_error_for_bedrock_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = bedrock_client.BedrockSettings(
        model_id="eu.amazon.nova-micro-v1:0",
        max_tokens=500,
        temperature=0.3,
    )

    def fail(*_: object, **__: object) -> str:
        raise bedrock_client.BedrockInvocationError(
            category="temporary_unavailable",
            status_code=503,
        )

    monkeypatch.setattr(handler, "load_bedrock_settings", lambda: settings)
    monkeypatch.setattr(handler, "generate_answer", fail)

    response = handler.lambda_handler(build_event(), FakeContext())

    assert response["statusCode"] == 503
    assert decode_body(response) == {
        "error": {
            "code": "LLM_ERROR",
            "message": "No se ha podido generar una respuesta.",
        }
    }


def test_lambda_handler_returns_internal_error_without_leaking_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = bedrock_client.BedrockSettings(
        model_id="eu.amazon.nova-micro-v1:0",
        max_tokens=500,
        temperature=0.3,
    )

    def crash(*_: object, **__: object) -> str:
        raise RuntimeError("boom-internal-details")

    monkeypatch.setattr(handler, "load_bedrock_settings", lambda: settings)
    monkeypatch.setattr(handler, "generate_answer", crash)

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


def test_lambda_handler_treats_missing_method_as_post_for_local_compatibility(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_bedrock_success(monkeypatch)

    event = build_event()
    event.pop("requestContext")
    response = handler.lambda_handler(event, FakeContext())

    assert response["statusCode"] == 200
