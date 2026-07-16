# Implementation Plan

## Project Objective

Build a simple serverless portfolio application where a user submits a question in a browser, a frontend sends that question to an AWS Lambda backend, and the backend returns an answer generated through Amazon Bedrock.

## Expected User Flow

1. A user opens the public website.
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
  -> S3 static website
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
```

## API Contract

Implemented public endpoint:

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
- Manual end-to-end checks when deployed infrastructure is involved

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

Current status:

- Completed on July 16, 2026 on branch `feature/bedrock-integration`.

### Phase 7. S3 frontend deployment

Objective:
Prepare and deploy the static frontend hosting path.

Main tasks:
- finalize visible frontend copy
- define S3 website infrastructure in the existing stack
- synchronize static frontend assets
- update backend CORS for the deployed website origin
- document the public website and deployment flow

Expected result:
The static frontend is available publicly from S3 website hosting and can call the Bedrock-backed backend.

Validation required:
- local frontend verification
- local quality checks
- stack update preview
- stack deployment
- S3 asset synchronization
- public browser verification

Manual user action expected:
No additional manual AWS approval was needed beyond existing deployment access.

Current status:
- Completed on July 16, 2026 on branch `feature/s3-frontend-deployment`.

Frontend hosting approach:
- Amazon S3 static website hosting

Selected bucket name:
- `aws-cloud-ai-web-herrerogusano-frontend`

Website URL:
- `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`

Configuration decision:
- keep `frontend/config.js` committed with the public Function URL
- exclude `frontend/config.example.js` from S3 sync

CORS decision:
- allow the exact S3 website origin
- keep `http://localhost:8000` for local development
- avoid wildcard origins now that the real origins are known

Important limitation:
- S3 static website hosting is HTTP only
- CloudFront could provide HTTPS later, but it was intentionally not added in this phase

Validation performed:
- `uv sync`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest`
- `uv run mypy .`
- `sam validate`
- `sam build`
- local frontend verification against the deployed Bedrock-backed Lambda
- stack update preview with `sam deploy --no-execute-changeset`
- stack update with `sam deploy`
- `powershell -ExecutionPolicy Bypass -File scripts/sync_frontend.ps1 -BucketName aws-cloud-ai-web-herrerogusano-frontend`
- public browser verification on the S3 website URL
- direct CORS preflight verification for the S3 website origin

Deployment result:
- the existing stack `aws-cloud-ai-web-backend` was updated successfully in `eu-west-1`
- the frontend bucket and bucket policy were added
- the public website served the static frontend and returned real Bedrock-backed answers through the existing Lambda

Deviation from original plan:
- no separate frontend stack was needed; the existing stack remained sufficient

### Phase 8. Pull Request CI

Objective:
Add Pull Request validation in GitHub Actions.

Main tasks:
- create a workflow for lint, format, tests, and type checking
- reuse the same checks already used locally
- keep deployment automation out of scope for this phase

Expected result:
Pull Requests receive automatic validation feedback.

Manual user action expected:
Yes. A remote GitHub repository already exists, so the remaining work is repository workflow configuration.

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
