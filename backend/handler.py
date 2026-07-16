"""AWS Lambda handler for the Bedrock-backed question answering flow."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Mapping
from typing import Protocol

from backend.bedrock_client import (
    BedrockInvocationError,
    generate_answer,
    load_bedrock_settings,
)
from backend.responses import error_response, json_response
from backend.validation import MAX_QUESTION_LENGTH, ValidationError, validate_question

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
                message="El cuerpo debe ser JSON valido.",
            ) from exc

        if not isinstance(parsed_body, dict):
            raise ValidationError(
                code="INVALID_REQUEST",
                message="El cuerpo debe ser un objeto JSON.",
            )

        return parsed_body

    raise ValidationError(
        code="INVALID_REQUEST",
        message="El cuerpo debe ser JSON valido.",
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
            message="Solo se admite el metodo POST.",
        )

    try:
        payload = parse_event_body(event)
        question = validate_question(payload, max_length=MAX_QUESTION_LENGTH)
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

    try:
        settings = load_bedrock_settings()
        started_at = time.perf_counter()
        logger.info(
            (
                "event=bedrock_invocation_started request_id=%s "
                "model_id=%s max_tokens=%s temperature=%s"
            ),
            request_id,
            settings.model_id,
            settings.max_tokens,
            settings.temperature,
        )
        answer = generate_answer(question, settings=settings)
    except BedrockInvocationError as exc:
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        logger.warning(
            "event=bedrock_invocation_failed request_id=%s category=%s model_id=%s duration_ms=%s",
            request_id,
            exc.category,
            settings.model_id,
            duration_ms,
        )
        return error_response(
            status_code=exc.status_code,
            code="LLM_ERROR",
            message=exc.public_message,
        )
    except Exception:
        logger.exception("event=request_failed request_id=%s code=INTERNAL_ERROR", request_id)
        return error_response(
            status_code=500,
            code="INTERNAL_ERROR",
            message="Ha ocurrido un error interno inesperado.",
        )

    duration_ms = int((time.perf_counter() - started_at) * 1000)
    logger.info(
        "event=bedrock_invocation_completed request_id=%s model_id=%s duration_ms=%s",
        request_id,
        settings.model_id,
        duration_ms,
    )
    logger.info("event=request_completed request_id=%s status_code=200", request_id)
    return json_response(
        status_code=200,
        payload={"answer": answer},
    )
