# aws-cloud-ai-web

`aws-cloud-ai-web` is a serverless portfolio project built in phases. The current application runs a local static frontend that sends real questions to a deployed AWS Lambda backend through a public Lambda Function URL, and the backend now generates the answer through Amazon Bedrock.

## Current Status

Phase 6 is complete as of July 16, 2026.

- Repository structure and Python tooling are in place.
- The frontend lives in `frontend/` and uses plain HTML, CSS, and JavaScript.
- The backend Lambda is deployed in `eu-west-1` through AWS SAM.
- The frontend performs a real `POST` request to the deployed Function URL.
- The backend calls Amazon Bedrock through the Converse API.
- The public API contract remains `{"answer":"..."}` on success.
- The frontend is still local only.
- There is still no S3 frontend deployment.
- There is still no CI/CD workflow in this phase.

## Current Implemented Architecture

```text
Local browser frontend
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
  -> Generated answer
```

More detail: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)

## Technology Choices

- Backend language: Python
- Dependency management: `uv`
- Testing: `pytest`
- Linting and formatting: `Ruff`
- Type checking: `mypy`
- Infrastructure as code: AWS SAM
- Frontend: plain HTML, CSS, and JavaScript
- Public backend endpoint: Lambda Function URL
- LLM provider: Amazon Bedrock
- Selected Bedrock model profile: `eu.amazon.nova-micro-v1:0`
- Planned frontend hosting: Amazon S3
- Planned CI/CD: GitHub Actions
- Git workflow: short-lived branches and Pull Requests
- Commit style: Conventional Commits
- AWS region: `eu-west-1`

## Bedrock Configuration

The Lambda reads its Bedrock configuration from environment variables defined in `template.yaml`.

- `BEDROCK_MODEL_ID`
- `BEDROCK_MAX_TOKENS`
- `BEDROCK_TEMPERATURE`

Current deployed values:

```text
BEDROCK_MODEL_ID=eu.amazon.nova-micro-v1:0
BEDROCK_MAX_TOKENS=500
BEDROCK_TEMPERATURE=0.3
```

Model selection summary:

- `eu.amazon.nova-micro-v1:0` is active in `eu-west-1`
- it supports the Converse API
- it was successfully invoked from the current AWS account before implementation
- it is a fast and relatively inexpensive text model suited to a simple interactive portfolio exercise
- it uses an inference profile, so IAM must allow the profile plus the linked foundation-model ARNs

## Local Prerequisites

- Python 3.13
- `uv`
- Git
- AWS CLI
- AWS SAM CLI

## Frontend Configuration

The frontend reads the backend URL from `frontend/config.js`.

- `frontend/config.js` is committed in this learning phase because the Function URL is already public and is not a secret.
- `frontend/config.example.js` provides the safe template shape.
- The URL is still treated as environment-specific configuration and should not be scattered through app logic.

Current committed Function URL:

- `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`

Configuration shape:

```javascript
window.APP_CONFIG = {
    apiUrl: "https://example.lambda-url.eu-west-1.on.aws/",
};
```

## Development Commands

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run mypy .
sam validate
sam build
python -m http.server 8000 --directory frontend
```

Then open `http://localhost:8000`.

If Python dependencies change and SAM must package them, refresh the deployment manifest with:

```bash
uv export --format requirements-txt --no-dev --output-file requirements.txt
```

To retrieve deployed stack outputs:

```bash
sam list stack-outputs --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

## Current Frontend Functionality

- Accepts one question in a multiline text area
- Rejects empty questions with client-side validation
- Validates the backend URL configuration before sending
- Sends a real `POST` request with `Content-Type: application/json`
- Uses `AbortController` with a 25-second timeout
- Prevents repeated submissions while a request is in progress
- Shows loading, success, and error states
- Renders backend text safely with `textContent`
- Preserves the current question after backend or network errors

## Current Backend Functionality

- Accepts `POST` requests only
- Parses JSON request bodies
- Validates the `question` field with a maximum of 1000 characters
- Calls Amazon Bedrock through `bedrock-runtime.converse`
- Uses a small fixed system prompt plus the validated user question
- Maps provider failures to controlled public errors
- Logs Bedrock start, completion, failure category, duration, model id, and request id
- Uses IAM-based AWS authentication only

Important:

- No external API key is used
- No streaming exists in this phase
- No chat history exists in this phase
- No frontend S3 deployment exists yet
- No CI/CD workflow exists yet

## Deployed Backend Endpoint

Current environment-specific Function URL:

- `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`

Example request:

```bash
curl -X POST "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is AWS Lambda?"}'
```

## Cost Warning

Amazon Bedrock usage is not guaranteed to be free.

- This phase uses `Amazon Nova Micro` because it is fast and comparatively low-cost for small text requests.
- Keep testing low-volume and intentional.
- Avoid repeated integration calls and load testing.
- Check the official AWS Nova pricing page before heavier usage.

## Security Limitations

- The Function URL is public and unauthenticated in this phase
- CORS is not authentication or authorization
- The backend trusts AWS IAM for Bedrock access, not an app secret
- This setup is acceptable for a learning exercise, not for sensitive production data

## Validation Summary

Verified in this phase:

- `uv sync`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest`
- `uv run mypy .`
- `sam validate`
- `sam build`
- Bedrock model availability and account access in `eu-west-1`
- Stack update preview and deploy of the existing backend stack
- Direct Function URL smoke test with a real Bedrock answer
- Local frontend browser verification with empty-input validation, loading state, generated answer, second request, and clean browser console
- CloudWatch log verification for Bedrock start and completion events

## Documentation

- Implementation plan: [docs/implementation-plan.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/implementation-plan.md)
- Architecture: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)
- API contract: [docs/api.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/api.md)
- Deployment notes: [docs/deployment.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/deployment.md)
- Teardown notes: [docs/teardown.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/teardown.md)
- Resource inventory: [docs/aws-resources.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/aws-resources.md)
- Architecture Decision Records: [docs/decisions](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/decisions)

## Next Planned Phase

The exact recommended next step is Phase 7 from the implementation plan: deploy the static frontend to Amazon S3 while keeping the Bedrock-backed backend and the current response contract stable.
