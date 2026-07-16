# aws-cloud-ai-web

`aws-cloud-ai-web` is a serverless portfolio project built in phases. The current application is publicly available as a static website hosted in Amazon S3, sends questions to a public AWS Lambda Function URL, and receives real answers generated through Amazon Bedrock.

## Current Status

The application is live and the repository now includes GitHub Actions workflows for Pull Request validation and automatic frontend deployment to S3 on pushes to `main`.

- Repository structure and Python tooling are in place.
- The frontend lives in `frontend/` and uses plain HTML, CSS, and JavaScript.
- The frontend is deployed publicly through an S3 static website bucket in `eu-west-1`.
- The backend Lambda is deployed in `eu-west-1` through AWS SAM.
- The public frontend performs a real `POST` request to the deployed Function URL.
- The backend calls Amazon Bedrock through the Converse API.
- The public API contract remains `{"answer":"..."}` on success.
- Pull Requests to `main` are validated by GitHub Actions.
- Frontend deployment to the existing S3 website bucket is automated through GitHub Actions OIDC.
- Backend deployment still remains manual through AWS SAM.

## Current Implemented Architecture

```text
User browser
  -> S3 static website
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
  -> Generated answer
```

More detail: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)

## Public Frontend

Current public website URL:

- `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`

Important limitation:

- this S3 static website endpoint is `HTTP`, not `HTTPS`
- this is acceptable for the current learning phase
- a future improvement could place CloudFront in front of the bucket to provide HTTPS, but that is explicitly out of scope for the current phase

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
- Frontend hosting: Amazon S3 static website hosting
- CI/CD: GitHub Actions for PR validation and frontend deployment
- Git workflow: short-lived branches and Pull Requests
- Commit style: Conventional Commits
- AWS region: `eu-west-1`

## Frontend Configuration

The frontend reads the backend URL from `frontend/config.js`.

Current configuration decision:

- `frontend/config.js` is committed with the public Lambda Function URL
- the Function URL is configuration, not a secret
- the URL is not duplicated across frontend files
- `frontend/config.example.js` is a local template and is excluded from the public S3 sync

Configuration shape:

```javascript
window.APP_CONFIG = {
    apiUrl: "https://example.lambda-url.eu-west-1.on.aws/",
};
```

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

## Local Prerequisites

- Python 3.13
- `uv`
- Git
- AWS CLI
- AWS SAM CLI

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

## Manual Deployment

Infrastructure update:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-confirm-changeset --no-fail-on-empty-changeset
```

Frontend asset sync:

```bash
powershell -ExecutionPolicy Bypass -File scripts/sync_frontend.ps1 -BucketName aws-cloud-ai-web-herrerogusano-frontend
```

To retrieve deployed outputs:

```bash
sam list stack-outputs --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

## GitHub Actions Deployment

The repository includes two workflow files:

- `.github/workflows/ci.yml`
- `.github/workflows/deploy-frontend.yml`

Implemented behavior:

- Pull Requests targeting `main` run `uv sync --frozen`, Ruff, `mypy`, `pytest`, `sam validate`, and `sam build`
- pushes to `main` rerun validation, assume an AWS role through GitHub OIDC, and deploy `frontend/` with `aws s3 sync --delete`
- the frontend deployment workflow does not deploy the backend Lambda

Required GitHub repository variables:

- `AWS_REGION=eu-west-1`
- `AWS_FRONTEND_BUCKET=aws-cloud-ai-web-herrerogusano-frontend`
- `AWS_DEPLOY_ROLE_ARN=<GitHub OIDC deployment role ARN>`

Bootstrap IAM for the workflow is defined separately in `bootstrap/github-frontend-deploy-iam.yaml`.

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
- Works from both the public S3 website origin and local development origin

## Current Backend Functionality

- Accepts `POST` requests only
- Parses JSON request bodies
- Validates the `question` field with a maximum of 1000 characters
- Calls Amazon Bedrock through `bedrock-runtime.converse`
- Uses a small fixed system prompt plus the validated user question
- Maps provider failures to controlled public errors
- Logs Bedrock start, completion, failure category, duration, model id, and request id
- Uses IAM-based AWS authentication only

## Cost Warning

Expected low-volume costs should stay small, but they are not guaranteed to be zero.

Relevant cost sources:

- S3 storage
- S3 requests
- Lambda invocations
- CloudWatch logs
- Bedrock inference

## Security Limitations

- the S3 website bucket is public-read by design for static asset delivery
- every file uploaded to that bucket should be considered public
- the Function URL is public and unauthenticated in this phase
- CORS is not authentication or authorization
- the backend trusts AWS IAM for Bedrock access, not an app secret
- the public website uses HTTP because S3 static website hosting does not provide HTTPS directly

## Validation Summary

Verified in this phase:

- `uv sync`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest`
- `uv run mypy .`
- `sam validate`
- `sam build`
- local frontend verification with final copy and real Bedrock answer
- stack update preview and deploy of the existing backend stack
- public S3 website asset sync
- public browser verification against the S3 website URL
- CORS preflight verification from the S3 website origin
- responsive mobile-width verification on the public website
- local workflow configuration tests for CI and frontend deployment

## Documentation

- Implementation plan: [docs/implementation-plan.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/implementation-plan.md)
- Architecture: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)
- API contract: [docs/api.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/api.md)
- Deployment notes: [docs/deployment.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/deployment.md)
- Teardown notes: [docs/teardown.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/teardown.md)
- Resource inventory: [docs/aws-resources.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/aws-resources.md)
- Architecture Decision Records: [docs/decisions](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/decisions)

## Next Planned Phase

The exact recommended next step after frontend CI/CD is automatic backend deployment through AWS SAM, keeping the same least-privilege and review-first approach.
