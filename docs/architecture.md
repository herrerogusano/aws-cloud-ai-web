# Architecture

This document describes the current implemented architecture for `aws-cloud-ai-web`.

## Current Architecture

Status: application flow implemented and repository delivery flow defined as of July 16, 2026.

```text
User browser
  -> S3 static website
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
  -> Generated answer
```

Additional local validation path:

```text
Local browser
  -> frontend/ served over HTTP
  -> same Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
```

Repository delivery flow:

```text
Feature branch
  -> Pull Request to main
  -> GitHub Actions CI
  -> merge to main
  -> GitHub Actions production deployment
  -> GitHub OIDC temporary AWS credentials
  -> AWS SAM / CloudFormation
  -> Lambda and infrastructure update
  -> aws s3 sync
  -> S3 static website
```

## Current Components

### Frontend

- Plain HTML, CSS, and JavaScript in `frontend/`
- Hosted publicly in S3 static website hosting
- Reads backend configuration from `frontend/config.js`
- Uses `fetch` plus `AbortController`
- Uses a 25-second browser timeout to stay above the 20-second Lambda timeout
- Renders success and error states without `innerHTML`

### Public frontend hosting

- Amazon S3 static website bucket
- Public read for static frontend assets only
- Current website URL:
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`
- HTTP only in this phase

### Public backend entry point

- AWS Lambda Function URL
- Public and unauthenticated in this educational phase
- CORS currently allows:
  - `http://localhost:8000`
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`

### Lambda backend

- Python handler in `backend.handler`
- Shared validation and response helpers
- Bedrock integration isolated in `backend.bedrock_client`
- Uses module-level lazy Bedrock client reuse without network calls during import

### Amazon Bedrock

- Runtime client: `bedrock-runtime`
- API style: Converse API
- Selected profile: `eu.amazon.nova-micro-v1:0`
- Authentication: Lambda execution role only

### Repository delivery

- Pull Request validation is defined in `.github/workflows/ci.yml`
- Production deployment is defined in `.github/workflows/deploy.yml`
- GitHub Actions assumes AWS credentials through OIDC only for trusted `main` deployments
- The backend deployment role is separate from the frontend deployment role
- `sam deploy` passes a separate CloudFormation execution role
- Frontend synchronization runs only after backend deployment succeeds

## Current API Shape

- Method: `POST`
- Path: `/`
- Request content type: `application/json`
- Request body:

```json
{
  "question": "What can you tell me about serverless architectures?"
}
```

- Success response:

```json
{
  "answer": "..."
}
```

- Error response:

```json
{
  "error": {
    "code": "LLM_ERROR",
    "message": "No se ha podido generar una respuesta."
  }
}
```

Detailed contract: [docs/api.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/api.md)

## Bedrock Request Design

The backend sends:

- one fixed system instruction
- one validated user message
- conservative inference settings

The application does not currently include:

- conversation memory
- tool use
- retrieval
- streaming

## Timeout Behavior

- Lambda timeout: `20` seconds
- Frontend request timeout: `25` seconds

This keeps normal browser requests from aborting before the Lambda reaches its own timeout budget.

## Error Flow

Validation or provider failures are translated as follows:

- invalid request or invalid JSON -> `400`
- wrong method -> `405`
- Bedrock temporary unavailability or throttling -> `503`
- Bedrock provider failure or invalid provider response -> `502`
- unexpected internal failure -> `500`

The frontend only receives controlled public messages and never raw AWS exception payloads.

## IAM Notes

The Lambda execution role includes:

- `bedrock:GetInferenceProfile` on the selected inference profile ARN
- `bedrock:InvokeModel` on the selected inference profile ARN
- `bedrock:InvokeModel` on the linked `amazon.nova-micro-v1:0` foundation-model ARNs for the profile regions
- a `bedrock:InferenceProfileArn` condition to keep the foundation-model permission tied to the selected profile

No broad Bedrock managed policy was attached.

## Security And Hosting Notes

- the frontend bucket is public-read and should contain only intended public assets
- public write is not allowed
- the backend remains publicly reachable through a Function URL
- CORS is not authentication
- the S3 static website endpoint is HTTP only
- the deployment workflow receives AWS credentials only on `push` to `main`
- the CI workflow receives no AWS credentials and no OIDC token
- the backend deployment role cannot modify the GitHub OIDC provider or its own trust relationship

## Still Not In Scope

- CloudFront
- Route 53
- API Gateway
- authentication
- database storage
- chat history
- automated rollback strategies beyond CloudFormation rollback

## Planned Next Phase

```text
project closure
  -> portfolio preparation
  -> final documentation pass
```

Status: planned only for the next phase after the production deployment pipeline is complete.
