# aws-cloud-ai-web

`aws-cloud-ai-web` is a planned serverless portfolio project. The target application is a static frontend that sends a user question to an AWS Lambda backend, and the backend will later call an LLM through Amazon Bedrock.

## Current Status

The repository is in project foundation only.

- Repository structure is prepared.
- Python tooling is configured with `uv`.
- Documentation and architecture decisions are recorded.
- No frontend, Lambda handler, AWS infrastructure, or GitHub Actions workflow has been implemented yet.
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
```

Notes:

- `mypy` was selected instead of Pyright to keep the initial toolchain Python-native and simple to run through `uv`.
- `boto3` is intentionally not installed as a production dependency at this stage. The planned backend will run on AWS Lambda, where the AWS SDK is commonly available already. If later implementation needs an explicit pinned SDK dependency, that decision can be revisited.

## Documentation

- Implementation plan: [docs/implementation-plan.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/implementation-plan.md)
- Planned architecture: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)
- Planned deployment notes: [docs/deployment.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/deployment.md)
- Planned teardown notes: [docs/teardown.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/teardown.md)
- Resource inventory: [docs/aws-resources.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/aws-resources.md)
- Architecture Decision Records: [docs/decisions](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/decisions)

## Next Planned Phase

The exact recommended next step is to start Phase 2 from the implementation plan: create the local frontend shell without backend integration.
