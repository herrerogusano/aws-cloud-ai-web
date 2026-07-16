"""Amazon Bedrock integration helpers for the Lambda backend."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, cast

import boto3
from botocore.exceptions import BotoCoreError, ClientError

BEDROCK_RUNTIME_SERVICE = "bedrock-runtime"
DEFAULT_MODEL_ID = "eu.amazon.nova-micro-v1:0"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.3
SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Answer the user's question clearly and concisely. "
    "Do not claim access to information or tools you do not have."
)
DEFAULT_PUBLIC_ERROR_MESSAGE = "No se ha podido generar una respuesta."

logger = logging.getLogger(__name__)

_bedrock_runtime_client: Any | None = None


@dataclass(frozen=True)
class BedrockSettings:
    model_id: str
    max_tokens: int
    temperature: float
    system_prompt: str = SYSTEM_PROMPT


@dataclass(frozen=True)
class BedrockInvocationError(Exception):
    category: str
    status_code: int
    public_message: str = DEFAULT_PUBLIC_ERROR_MESSAGE


def parse_max_tokens(value: str | None) -> int:
    if value is None or not value.strip():
        return DEFAULT_MAX_TOKENS

    parsed_value = int(value)
    if parsed_value <= 0:
        raise ValueError("BEDROCK_MAX_TOKENS must be greater than zero.")
    return parsed_value


def parse_temperature(value: str | None) -> float:
    if value is None or not value.strip():
        return DEFAULT_TEMPERATURE

    parsed_value = float(value)
    if parsed_value < 0 or parsed_value > 1:
        raise ValueError("BEDROCK_TEMPERATURE must be between 0 and 1.")
    return parsed_value


def load_bedrock_settings() -> BedrockSettings:
    model_id = os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID).strip()
    if not model_id:
        raise RuntimeError("BEDROCK_MODEL_ID must not be empty.")

    return BedrockSettings(
        model_id=model_id,
        max_tokens=parse_max_tokens(os.getenv("BEDROCK_MAX_TOKENS")),
        temperature=parse_temperature(os.getenv("BEDROCK_TEMPERATURE")),
    )


def create_bedrock_runtime_client() -> Any:
    return boto3.client(BEDROCK_RUNTIME_SERVICE, region_name=os.getenv("AWS_REGION", "eu-west-1"))


def get_bedrock_runtime_client() -> Any:
    global _bedrock_runtime_client

    if _bedrock_runtime_client is None:
        _bedrock_runtime_client = create_bedrock_runtime_client()

    return _bedrock_runtime_client


def build_converse_request(question: str, settings: BedrockSettings) -> dict[str, object]:
    return {
        "modelId": settings.model_id,
        "system": [
            {
                "text": settings.system_prompt,
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": question,
                    }
                ],
            }
        ],
        "inferenceConfig": {
            "maxTokens": settings.max_tokens,
            "temperature": settings.temperature,
        },
    }


def extract_generated_text(response: dict[str, object]) -> str:
    output = response.get("output")
    if not isinstance(output, dict):
        raise BedrockInvocationError(category="invalid_response", status_code=502)

    message = output.get("message")
    if not isinstance(message, dict):
        raise BedrockInvocationError(category="invalid_response", status_code=502)

    content = message.get("content")
    if not isinstance(content, list):
        raise BedrockInvocationError(category="invalid_response", status_code=502)

    for block in content:
        if not isinstance(block, dict):
            continue
        text = block.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()

    raise BedrockInvocationError(category="invalid_response", status_code=502)


def map_bedrock_error(error: ClientError | BotoCoreError) -> BedrockInvocationError:
    if isinstance(error, BotoCoreError):
        return BedrockInvocationError(category="provider_failure", status_code=502)

    error_code = error.response.get("Error", {}).get("Code", "Unknown")

    if error_code in {"AccessDeniedException"}:
        return BedrockInvocationError(category="access_denied", status_code=502)

    if error_code in {"ResourceNotFoundException", "ValidationException"}:
        return BedrockInvocationError(category="model_unavailable", status_code=502)

    if error_code in {
        "ModelNotReadyException",
        "ModelTimeoutException",
        "ServiceUnavailableException",
        "ThrottlingException",
    }:
        return BedrockInvocationError(category="temporary_unavailable", status_code=503)

    return BedrockInvocationError(category="provider_failure", status_code=502)


def generate_answer(
    question: str,
    *,
    client: Any | None = None,
    settings: BedrockSettings | None = None,
) -> str:
    resolved_settings = settings or load_bedrock_settings()
    resolved_client = client or get_bedrock_runtime_client()
    request = build_converse_request(question, resolved_settings)

    try:
        response = cast(dict[str, object], resolved_client.converse(**request))
    except (ClientError, BotoCoreError) as error:
        logger.warning("event=bedrock_provider_error category=mapped")
        raise map_bedrock_error(error) from error

    return extract_generated_text(response)
