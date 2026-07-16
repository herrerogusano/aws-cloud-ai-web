# aws-cloud-ai-web

`aws-cloud-ai-web` is a planned serverless portfolio project. The target application is a static frontend that sends a user question to an AWS Lambda backend, and the backend will later call an LLM through Amazon Bedrock.

## Current Status

The repository now includes the local frontend shell, the local Lambda handler, and a deployed AWS backend for Phase 4.

- Repository structure and Python tooling are prepared.
- A local frontend exists in `frontend/` using plain HTML, CSS, and JavaScript.
- The backend Lambda is deployed in `eu-west-1` through AWS SAM.
- The backend exposes a public Lambda Function URL and still returns a fixed simulated response.
- The frontend is still not connected to the deployed backend yet.

## Planned Architecture

This architecture is planned and not yet deployed.

```text
User
  -> Static frontend in S3
  -> HTTPS request
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
  -> AWS Lambda
  -> Frontend response
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
- Planned LLM provider: Amazon Bedrock
- Planned frontend hosting: Amazon S3
- Planned CI/CD: GitHub Actions
- Git workflow: short-lived branches and Pull Requests
- Commit style: Conventional Commits
- Planned AWS region: `eu-west-1`

## Local Prerequisites

- Python 3.13
- `uv`
- Git
- AWS SAM CLI for future infrastructure validation and deployment steps
- AWS CLI for future AWS authentication and deployment steps

## Development Commands

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
python -m http.server 8000 --directory frontend
```

Then open `http://127.0.0.1:8000`.

For local error-state testing, open `http://127.0.0.1:8000/?simulateError=1`.

To invoke the backend directly without AWS tooling:

```bash
python -c "from backend.handler import lambda_handler; event={'version':'2.0','requestContext':{'http':{'method':'POST'}},'isBase64Encoded':False,'body':'{\"question\":\"¿Qué es AWS Lambda?\"}'}; print(lambda_handler(event, None))"
```

Useful test event fixtures are available in `events/`.

To retrieve deployed stack outputs:

```bash
sam list stack-outputs --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

Notes:

- `mypy` was selected instead of Pyright to keep the initial toolchain Python-native and simple to run through `uv`.
- `boto3` is intentionally not installed as a production dependency at this stage. The planned backend will run on AWS Lambda, where the AWS SDK is commonly available already. If later implementation needs an explicit pinned SDK dependency, that decision can be revisited.

## Current Frontend Functionality

- Accepts one question in a multiline text area
- Rejects empty questions with client-side validation
- Prevents repeated submissions while a simulated response is in progress
- Shows a visible loading state
- Displays a simulated success response with safe text rendering
- Displays a simulated error message when `?simulateError=1` is present

Important:

- Responses are simulated locally
- No real HTTP request is made
- No Lambda Function URL is configured yet

## Current Backend Functionality

- Accepts local Lambda-style events
- Supports `POST` requests only
- Parses JSON request bodies
- Validates the `question` field with a maximum of 1000 characters
- Returns a fixed JSON answer that clearly indicates the response is temporary
- Returns consistent JSON errors with status codes and CORS headers

Important:

- The backend response is still fixed
- No Amazon Bedrock call is made
- The frontend is not connected to this backend yet

## Deployed Backend Endpoint

Current environment-specific Function URL:

- `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`

Example request:

```bash
curl -X POST "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Content-Type: application/json" \
  -d '{"question":"Que es AWS Lambda?"}'
```

Security limitations:

- The Function URL is public and unauthenticated in this phase
- CORS is not authentication or authorization
- This endpoint is acceptable for a learning exercise, not for sensitive production data

## Documentation

- Implementation plan: [docs/implementation-plan.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/implementation-plan.md)
- Planned architecture: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)
- Local API contract: [docs/api.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/api.md)
- Deployment notes: [docs/deployment.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/deployment.md)
- Teardown notes: [docs/teardown.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/teardown.md)
- Resource inventory: [docs/aws-resources.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/aws-resources.md)
- Architecture Decision Records: [docs/decisions](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/decisions)

## Next Planned Phase

The exact recommended next step is to start Phase 5 from the implementation plan: connect the frontend to the deployed Lambda Function URL while keeping the backend response fixed.
