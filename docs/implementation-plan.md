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

## Initial Architecture

```text
Browser
  -> S3-hosted static frontend
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
```

The architecture remains planned only until AWS resources are explicitly created.

## API Contract

Planned public endpoint:

- Method: `POST`
- Path: `/`
- Content-Type: `application/json`

Planned request body:

```json
{
  "question": "string"
}
```

Planned success response:

```json
{
  "answer": "string"
}
```

Planned error response:

```json
{
  "error": "string"
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
- Add integration-style validation only when the backend and frontend exist

## CI/CD Strategy

- Use short-lived branches and Pull Requests
- Run local quality checks first
- Later add GitHub Actions for lint, format, tests, and type checks
- Add deployment automation only after infrastructure and application paths are stable

## AWS Cost Precautions

- Prefer the smallest possible serverless footprint
- Avoid deploying until local validation is complete
- Keep Bedrock usage explicit and test only when needed
- Track created resources in `docs/aws-resources.md`
- Add teardown guidance alongside every new resource introduced later

## Definition Of Done

The project is done when:

- The frontend can submit a question successfully
- The backend can validate input and return a Bedrock-backed response
- The application is deployed through the documented AWS path
- Basic CI validation runs on Pull Requests
- The repository documentation matches the implemented system
- AWS resources and teardown steps are documented

## Phased Roadmap

### Phase 1. Project foundation

Objective:
Prepare the repository, tooling, documentation, and durable project context.

Main tasks:
- Create the repository structure.
- Configure `uv`, `pytest`, `Ruff`, and `mypy`.
- Document the planned architecture and roadmap.
- Record initial ADRs and vault context.

Expected result:
The project can be developed consistently, but no application functionality exists yet.

Validation required:
- `uv sync`
- `uv run pytest`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy .`
- `sam validate` when SAM CLI becomes available

Manual user action expected:
Yes. The local machine needs AWS SAM CLI installed before `sam validate` can run.

### Phase 2. Local frontend shell

Objective:
Create the static frontend shell without backend integration.

Main tasks:
- Add the initial HTML structure.
- Add CSS for a simple portfolio-quality layout.
- Add frontend JavaScript structure without live API calls.

Expected result:
The frontend can render locally and collect a question from the user.

Validation required:
- Manual browser verification
- Frontend file review

Manual user action expected:
No.

Current status:
- Completed on branch `feature/frontend-shell`.

Validation performed:
- Local static file review
- `pytest` checks for HTML structure, JavaScript syntax, success flow, error flow, loading reset, and safe text rendering
- Browser automation against a local HTTP server using Playwright already available in the environment

Deviation from original plan:
- Added lightweight browser automation through existing tooling to validate the frontend behavior more thoroughly without introducing new project dependencies.

### Phase 3. Local Lambda handler with fixed response

Objective:
Create the backend entry point locally with a fixed response.

Main tasks:
- Add a Lambda handler module.
- Validate request parsing.
- Return a fixed JSON response without Bedrock.
- Add backend unit tests.

Expected result:
The backend can handle the planned request contract locally.

Validation required:
- `pytest`
- `mypy`
- `Ruff`

Manual user action expected:
No.

Current status:
- Completed on branch `feature/lambda-basic-handler`.

Validation performed:
- `uv run pytest`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy .`
- Direct Python invocation of `backend.handler.lambda_handler`

Deviation from original plan:
- Added reusable response and validation helpers to keep the Lambda response contract consistent without introducing any framework.

Manual checks still pending:
- `sam validate`, `sam build`, and `sam local invoke` are blocked until AWS SAM CLI is installed locally.

### Phase 4. AWS SAM backend infrastructure

Objective:
Define and validate the backend infrastructure in AWS SAM.

Main tasks:
- Add Lambda resource definitions.
- Add Lambda Function URL configuration.
- Add minimal IAM permissions.
- Validate the SAM template locally.

Expected result:
Infrastructure as code exists for the backend, but resources are not yet assumed to be deployed.

Validation required:
- `sam validate`
- Template review

Manual user action expected:
Yes. AWS SAM CLI and AWS credentials will be needed for later deployment-related verification.

### Phase 5. Frontend-to-backend integration

Objective:
Connect the frontend to the backend contract.

Main tasks:
- Add frontend fetch logic.
- Handle loading, success, and error states.
- Align request and response behavior with backend tests.

Expected result:
The frontend can call the backend and render the fixed response.

Validation required:
- Manual browser testing
- Backend tests

Manual user action expected:
No.

### Phase 6. Amazon Bedrock integration

Objective:
Replace the fixed backend response with Bedrock inference.

Main tasks:
- Add Bedrock client integration.
- Handle model request and response mapping.
- Add failure handling for Bedrock access issues.
- Revisit dependency choices if the runtime needs explicit SDK packaging.

Expected result:
The backend returns an actual model answer through Amazon Bedrock.

Validation required:
- Backend tests where practical
- Manual integration verification

Manual user action expected:
Yes. Bedrock model access must be enabled and verified by the user in the target AWS account.

### Phase 7. S3 frontend deployment

Objective:
Prepare and deploy the static frontend hosting path.

Main tasks:
- Define the frontend deployment approach.
- Create the S3 hosting workflow.
- Document the deployed URL once it exists.

Expected result:
The static frontend is available from S3 hosting.

Validation required:
- Manual browser verification against the deployed frontend
- Resource inventory update

Manual user action expected:
Yes. AWS deployment access is required.

### Phase 8. Pull Request CI

Objective:
Add Pull Request validation in GitHub Actions.

Main tasks:
- Create a workflow for tests, lint, format, and type checking.
- Run the same checks already used locally.
- Keep secrets out of the workflow unless later required.

Expected result:
Pull Requests receive automatic validation feedback.

Validation required:
- Workflow syntax review
- CI run on a Pull Request

Manual user action expected:
Yes. A remote GitHub repository is required.

### Phase 9. Automatic deployment

Objective:
Automate deployment after merges to the main branch.

Main tasks:
- Add a deployment workflow.
- Configure GitHub secrets or OIDC-based access.
- Deploy the backend with AWS SAM.
- Synchronize frontend assets to S3.

Expected result:
A merge to `main` can trigger controlled deployment automation.

Validation required:
- Workflow run review
- Deployment verification

Manual user action expected:
Yes. Repository configuration and AWS deployment permissions are required.

### Phase 10. Portfolio documentation and project closure

Objective:
Finalize portfolio-facing documentation and close the project cleanly.

Main tasks:
- Update the README with implemented behavior.
- Finalize architecture and AWS resource inventory.
- Finalize teardown guidance.
- Document lessons learned and tradeoffs.

Expected result:
The repository clearly demonstrates the finished portfolio project.

Validation required:
- Documentation review
- Final end-to-end smoke test

Manual user action expected:
No, unless a final deployment verification is still pending.
