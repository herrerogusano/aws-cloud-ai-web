"""Local AWS Lambda handler with fixed response behavior."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Protocol

from backend.responses import error_response, json_response
from backend.validation import MAX_QUESTION_LENGTH, ValidationError, validate_question

logger = logging.getLogger(__name__)


class LambdaContext(Protocol):
    aws_request_id: str


def get_request_id(context: LambdaContext | None) -> str:
    if context is None:
        return "local-no-context"

    request_id = getattr(context, "aws_request_id", None)
    if isinstance(request_id, str) and request_id:
        return request_id
    return "local-no-request-id"


def detect_http_method(event: Mapping[str, object]) -> str:
    request_context = event.get("requestContext")
    if isinstance(request_context, Mapping):
        http_data = request_context.get("http")
        if isinstance(http_data, Mapping):
            method = http_data.get("method")
            if isinstance(method, str) and method:
                return method.upper()

    method = event.get("httpMethod")
    if isinstance(method, str) and method:
        return method.upper()

    return "POST"


def parse_event_body(event: Mapping[str, object]) -> dict[str, object]:
    if event.get("isBase64Encoded") is True:
        raise ValidationError(
            code="INVALID_REQUEST",
            message="No se admiten cuerpos en base64 en esta fase local.",
        )

    body = event.get("body")

    if body is None:
        raise ValidationError(
            code="INVALID_REQUEST",
            message="La pregunta es obligatoria.",
        )

    if isinstance(body, Mapping):
        return dict(body)

    if isinstance(body, str):
        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ValidationError(
                code="INVALID_JSON",
                message="El cuerpo debe ser JSON válido.",
            ) from exc

        if not isinstance(parsed_body, dict):
            raise ValidationError(
                code="INVALID_REQUEST",
                message="El cuerpo debe ser un objeto JSON.",
            )

        return parsed_body

    raise ValidationError(
        code="INVALID_REQUEST",
        message="El cuerpo debe ser JSON válido.",
    )


def build_fixed_answer(question: str) -> str:
    return (
        "Esta es una respuesta simulada del backend para la pregunta: "
        f"«{question}». "
        "La integración con Amazon Bedrock se añadirá en una fase posterior."
    )


def lambda_handler(
    event: Mapping[str, object],
    context: LambdaContext | None,
) -> dict[str, object]:
    request_id = get_request_id(context)
    method = detect_http_method(event)

    logger.info("event=request_received request_id=%s method=%s", request_id, method)

    if method != "POST":
        logger.warning(
            "event=request_validation_failed request_id=%s code=METHOD_NOT_ALLOWED method=%s",
            request_id,
            method,
        )
        return error_response(
            status_code=405,
            code="METHOD_NOT_ALLOWED",
            message="Solo se admite el método POST.",
        )

    try:
        payload = parse_event_body(event)
        question = validate_question(payload, max_length=MAX_QUESTION_LENGTH)
        answer = build_fixed_answer(question)
    except ValidationError as exc:
        logger.warning(
            "event=request_validation_failed request_id=%s code=%s",
            request_id,
            exc.code,
        )
        return error_response(
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
        )
    except Exception:
        logger.exception("event=request_failed request_id=%s code=INTERNAL_ERROR", request_id)
        return error_response(
            status_code=500,
            code="INTERNAL_ERROR",
            message="Ha ocurrido un error interno inesperado.",
        )

    logger.info("event=request_completed request_id=%s status_code=200", request_id)
    return json_response(
        status_code=200,
        payload={"answer": answer},
    )
