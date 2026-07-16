# Implementation Plan

## Project Objective

Build a simple serverless portfolio application where a user submits a question in a browser, a frontend sends that question to an AWS Lambda backend, and the backend returns an answer generated through Amazon Bedrock.

## Expected User Flow

1. A user opens the static website.
2. The user enters a question.
3. The frontend sends the question to the backend over HTTPS.
4. The backend validates the request and calls Amazon Bedrock.
5. The backend returns an answer.
6. The frontend renders the answer or an error state.

## Scope

- One static frontend
- One public Lambda backend entry point
- One Bedrock-backed question-and-answer flow
- Infrastructure managed through AWS SAM
- Basic CI validation for code quality
- Deployment automation after the application works locally

## Non-Goals

- Multi-page frontend application
- User authentication
- Database storage
- Conversation history
- Streaming responses
- Model fine-tuning
- Multi-region deployment
- Production hardening beyond a portfolio-appropriate baseline

## Current Architecture

```text
Browser
  -> Local static frontend
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
```

## API Contract

Planned and now implemented public endpoint:

- Method: `POST`
- Path: `/`
- Content-Type: `application/json`

Request body:

```json
{
  "question": "string"
}
```

Success response:

```json
{
  "answer": "string"
}
```

Error response:

```json
{
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

## Security Principles

- Never commit secrets or credentials
- Validate and sanitize incoming request data
- Keep the public interface as small as possible
- Apply least privilege when IAM resources are added
- Avoid exposing sensitive backend details in frontend responses

## Testing Strategy

- `pytest` for backend unit tests
- `Ruff` for linting and formatting checks
- `mypy` for static type checking
- Local validation before opening a Pull Request
- Manual end-to-end checks when the deployed backend is involved

## CI/CD Strategy

- Use short-lived branches and Pull Requests
- Run local quality checks first
- Later add GitHub Actions for lint, format, tests, and type checking
- Add deployment automation only after infrastructure and application paths are stable

## AWS Cost Precautions

- Prefer the smallest possible serverless footprint
- Keep Bedrock usage explicit and test only when needed
- Track created resources in `docs/aws-resources.md`
- Add teardown guidance alongside every new resource introduced later

## Definition Of Done

The project is done when:

- the frontend can submit a question successfully
- the backend can validate input and return a Bedrock-backed response
- the application is deployed through the documented AWS path
- basic CI validation runs on Pull Requests
- the repository documentation matches the implemented system
- AWS resources and teardown steps are documented

## Phased Roadmap

### Phase 1. Project foundation

Current status:

- Completed.

### Phase 2. Local frontend shell

Current status:

- Completed on branch `feature/frontend-shell`.

### Phase 3. Local Lambda handler with fixed response

Current status:

- Completed on branch `feature/lambda-basic-handler`.

### Phase 4. AWS SAM backend infrastructure

Current status:

- Completed on July 16, 2026 on branch `feature/sam-backend-deployment`.

### Phase 5. Frontend-to-backend integration

Current status:

- Completed on July 16, 2026 on branch `feature/frontend-api-integration`.

### Phase 6. Amazon Bedrock integration

Objective:
Replace the fixed backend response with Bedrock inference.

Main tasks:
- add Bedrock client integration
- handle model request and response mapping
- add failure handling for Bedrock access issues
- make model configuration explicit
- update IAM and deployment docs accordingly

Expected result:
The backend returns an actual model answer through Amazon Bedrock.

Validation required:
- backend tests with mocks
- local quality checks
- deployment of the existing stack
- direct endpoint smoke test
- local frontend browser verification
- CloudWatch log verification

Manual user action expected:
Only if the selected model required access enablement or billing approval. That was not required for the chosen model in this phase.

Current status:
- Completed on July 16, 2026 on branch `feature/bedrock-integration`.

Selected model:
- `eu.amazon.nova-micro-v1:0`

Selection reasoning:
- available and active in `eu-west-1`
- compatible with the Converse API
- successfully invoked from the current AWS account before implementation
- suitable for simple question answering
- relatively inexpensive and fast for a portfolio exercise

Dependency decision:
- package `boto3` with the application instead of relying on the managed runtime version
- export `requirements.txt` from `uv` so AWS SAM actually includes the pinned SDK in the deployed artifact

Validation performed:
- `aws bedrock list-foundation-models --region eu-west-1`
- `aws bedrock get-foundation-model --region eu-west-1 --model-identifier amazon.nova-micro-v1:0`
- `aws bedrock list-inference-profiles --region eu-west-1`
- `aws bedrock-runtime converse --region eu-west-1 --cli-input-json ...`
- `uv sync`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest`
- `uv run mypy .`
- `sam validate`
- `sam build`
- stack update preview with `sam deploy --no-execute-changeset`
- stack update with `sam deploy`
- direct Function URL smoke test returning a generated answer
- local frontend browser verification with two successful requests
- CloudWatch log verification

Deployment result:
- the existing stack `aws-cloud-ai-web-backend` was updated successfully in `eu-west-1`
- CloudFormation changes were limited to the Lambda function and its IAM role

Deviation from original plan:
- the chosen Bedrock target had to be an inference profile rather than direct on-demand model invocation
- packaging `boto3` required adding a generated `requirements.txt` because SAM does not package dependencies directly from `pyproject.toml`

### Phase 7. S3 frontend deployment

Objective:
Prepare and deploy the static frontend hosting path.

Main tasks:
- define the frontend deployment approach
- create the S3 hosting workflow
- document the deployed URL once it exists

Expected result:
The static frontend is available from S3 hosting.

Validation required:
- manual browser verification against the deployed frontend
- resource inventory update

Manual user action expected:
Yes. AWS deployment access is required.

### Phase 8. Pull Request CI

Objective:
Add Pull Request validation in GitHub Actions.

Status:
- Planned only.

### Phase 9. Automatic deployment

Objective:
Automate deployment after merges to the main branch.

Status:
- Planned only.

### Phase 10. Portfolio documentation and project closure

Objective:
Finalize portfolio-facing documentation and close the project cleanly.

Status:
- Planned only.
