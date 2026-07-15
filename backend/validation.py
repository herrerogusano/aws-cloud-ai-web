"""Validation helpers for the local Lambda handler."""

from __future__ import annotations

from dataclasses import dataclass

MAX_QUESTION_LENGTH = 1000


@dataclass(frozen=True)
class ValidationError(Exception):
    code: str
    message: str
    status_code: int = 400


def validate_question(payload: object, max_length: int = MAX_QUESTION_LENGTH) -> str:
    if not isinstance(payload, dict):
        raise ValidationError(
            code="INVALID_REQUEST",
            message="El cuerpo debe ser un objeto JSON.",
        )

    question = payload.get("question")
    if question is None:
        raise ValidationError(
            code="INVALID_REQUEST",
            message="La pregunta es obligatoria.",
        )

    if not isinstance(question, str):
        raise ValidationError(
            code="INVALID_REQUEST",
            message="La pregunta debe ser un texto.",
        )

    normalized_question = question.strip()
    if not normalized_question:
        raise ValidationError(
            code="INVALID_REQUEST",
            message="La pregunta es obligatoria.",
        )

    if len(normalized_question) > max_length:
        raise ValidationError(
            code="QUESTION_TOO_LONG",
            message=f"La pregunta no puede superar los {max_length} caracteres.",
        )

    return normalized_question
