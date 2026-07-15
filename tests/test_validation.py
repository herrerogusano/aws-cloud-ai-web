import pytest

from backend.validation import MAX_QUESTION_LENGTH, ValidationError, validate_question


def test_validate_question_returns_trimmed_question() -> None:
    assert validate_question({"question": "  hola  "}) == "hola"


@pytest.mark.parametrize(
    ("payload", "code", "message"),
    [
        ({}, "INVALID_REQUEST", "La pregunta es obligatoria."),
        ({"question": ""}, "INVALID_REQUEST", "La pregunta es obligatoria."),
        ({"question": "   "}, "INVALID_REQUEST", "La pregunta es obligatoria."),
        ({"question": 123}, "INVALID_REQUEST", "La pregunta debe ser un texto."),
        ([], "INVALID_REQUEST", "El cuerpo debe ser un objeto JSON."),
    ],
)
def test_validate_question_rejects_invalid_payloads(
    payload: object,
    code: str,
    message: str,
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        validate_question(payload)

    assert exc_info.value.code == code
    assert exc_info.value.message == message


def test_validate_question_rejects_excessive_length() -> None:
    with pytest.raises(ValidationError) as exc_info:
        validate_question({"question": "a" * (MAX_QUESTION_LENGTH + 1)})

    assert exc_info.value.code == "QUESTION_TOO_LONG"
