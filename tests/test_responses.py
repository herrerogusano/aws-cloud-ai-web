import json

from backend.responses import DEFAULT_HEADERS, error_response, json_response


def decode_body(response: dict[str, object]) -> dict[str, object]:
    body = response["body"]
    assert isinstance(body, str)
    parsed_body = json.loads(body)
    assert isinstance(parsed_body, dict)
    return parsed_body


def test_json_response_has_json_body_and_default_headers() -> None:
    response = json_response(status_code=200, payload={"answer": "ok"})

    assert response["statusCode"] == 200
    assert response["headers"] == DEFAULT_HEADERS
    assert decode_body(response) == {"answer": "ok"}


def test_error_response_wraps_error_payload() -> None:
    response = error_response(
        status_code=400,
        code="INVALID_REQUEST",
        message="La pregunta es obligatoria.",
    )

    assert response["statusCode"] == 400
    assert decode_body(response) == {
        "error": {
            "code": "INVALID_REQUEST",
            "message": "La pregunta es obligatoria.",
        }
    }
