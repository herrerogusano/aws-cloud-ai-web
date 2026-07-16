from __future__ import annotations

import pytest
from botocore.exceptions import BotoCoreError, ClientError

from backend import bedrock_client


class FakeBedrockClient:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.last_request: dict[str, object] | None = None

    def converse(self, **kwargs: object) -> dict[str, object]:
        self.last_request = dict(kwargs)
        return self.response


def make_client_error(code: str, message: str = "failure") -> ClientError:
    return ClientError(
        error_response={"Error": {"Code": code, "Message": message}},
        operation_name="Converse",
    )


def test_generate_answer_builds_expected_converse_request() -> None:
    client = FakeBedrockClient(
        {
            "output": {
                "message": {
                    "content": [
                        {
                            "text": "Respuesta generada",
                        }
                    ]
                }
            }
        }
    )
    settings = bedrock_client.BedrockSettings(
        model_id="eu.amazon.nova-micro-v1:0",
        max_tokens=321,
        temperature=0.2,
    )

    answer = bedrock_client.generate_answer(
        "Explica Lambda",
        client=client,
        settings=settings,
    )

    assert answer == "Respuesta generada"
    assert client.last_request == {
        "modelId": "eu.amazon.nova-micro-v1:0",
        "system": [{"text": bedrock_client.SYSTEM_PROMPT}],
        "messages": [{"role": "user", "content": [{"text": "Explica Lambda"}]}],
        "inferenceConfig": {"maxTokens": 321, "temperature": 0.2},
    }


@pytest.mark.parametrize(
    "response",
    [
        {},
        {"output": {}},
        {"output": {"message": {}}},
        {"output": {"message": {"content": []}}},
        {"output": {"message": {"content": [{"text": "   "}]}}},
    ],
)
def test_extract_generated_text_rejects_invalid_provider_response(
    response: dict[str, object],
) -> None:
    with pytest.raises(bedrock_client.BedrockInvocationError) as exc_info:
        bedrock_client.extract_generated_text(response)

    assert exc_info.value.category == "invalid_response"
    assert exc_info.value.status_code == 502


@pytest.mark.parametrize(
    ("error_code", "category", "status_code"),
    [
        ("AccessDeniedException", "access_denied", 502),
        ("ResourceNotFoundException", "model_unavailable", 502),
        ("ValidationException", "model_unavailable", 502),
        ("ThrottlingException", "temporary_unavailable", 503),
        ("ServiceUnavailableException", "temporary_unavailable", 503),
        ("ModelTimeoutException", "temporary_unavailable", 503),
    ],
)
def test_map_bedrock_error_handles_client_errors(
    error_code: str,
    category: str,
    status_code: int,
) -> None:
    mapped = bedrock_client.map_bedrock_error(make_client_error(error_code))

    assert mapped.category == category
    assert mapped.status_code == status_code
    assert mapped.public_message == "No se ha podido generar una respuesta."


def test_map_bedrock_error_handles_botocore_errors() -> None:
    mapped = bedrock_client.map_bedrock_error(BotoCoreError())

    assert mapped.category == "provider_failure"
    assert mapped.status_code == 502


def test_generate_answer_raises_controlled_error_for_provider_failure() -> None:
    class RaisingClient:
        def converse(self, **_: object) -> dict[str, object]:
            raise make_client_error("AccessDeniedException")

    with pytest.raises(bedrock_client.BedrockInvocationError) as exc_info:
        bedrock_client.generate_answer(
            "Pregunta",
            client=RaisingClient(),
            settings=bedrock_client.BedrockSettings(
                model_id="eu.amazon.nova-micro-v1:0",
                max_tokens=500,
                temperature=0.3,
            ),
        )

    assert exc_info.value.category == "access_denied"
    assert exc_info.value.status_code == 502


def test_load_bedrock_settings_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BEDROCK_MODEL_ID", "custom-model")
    monkeypatch.setenv("BEDROCK_MAX_TOKENS", "123")
    monkeypatch.setenv("BEDROCK_TEMPERATURE", "0.6")

    settings = bedrock_client.load_bedrock_settings()

    assert settings == bedrock_client.BedrockSettings(
        model_id="custom-model",
        max_tokens=123,
        temperature=0.6,
    )


@pytest.mark.parametrize(
    ("env_name", "env_value"),
    [
        ("BEDROCK_MAX_TOKENS", "0"),
        ("BEDROCK_TEMPERATURE", "2"),
    ],
)
def test_load_bedrock_settings_rejects_invalid_environment_values(
    monkeypatch: pytest.MonkeyPatch,
    env_name: str,
    env_value: str,
) -> None:
    monkeypatch.setenv("BEDROCK_MODEL_ID", "custom-model")
    monkeypatch.setenv(env_name, env_value)

    with pytest.raises(ValueError):
        bedrock_client.load_bedrock_settings()
