# aws-cloud-ai-web

`aws-cloud-ai-web` is a planned serverless portfolio project. The target application is a static frontend that sends a user question to an AWS Lambda backend, and the backend will later call an LLM through Amazon Bedrock.

## Current Status

The repository now includes the local frontend shell for Phase 2.

- Repository structure and Python tooling are prepared.
- A local frontend exists in `frontend/` using plain HTML, CSS, and JavaScript.
- The current frontend validates input, shows a loading state, returns a simulated response, and can simulate an error.
- No backend, Lambda handler, AWS infrastructure, or GitHub Actions workflow has been implemented yet.
- Nothing has been deployed and no AWS resources have been created for this project.

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

## Documentation

- Implementation plan: [docs/implementation-plan.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/implementation-plan.md)
- Planned architecture: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)
- Planned deployment notes: [docs/deployment.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/deployment.md)
- Planned teardown notes: [docs/teardown.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/teardown.md)
- Resource inventory: [docs/aws-resources.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/aws-resources.md)
- Architecture Decision Records: [docs/decisions](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/decisions)

## Next Planned Phase

The exact recommended next step is to start Phase 3 from the implementation plan: implement the local Lambda handler with a fixed response and no Bedrock integration yet.
