# Architecture

This document describes the current implemented architecture and the next planned target architecture for `aws-cloud-ai-web`.

## Current Architecture

Status: implemented as of Phase 5.

```text
Local browser frontend
  -> Local static files served over HTTP
  -> Lambda Function URL
  -> AWS Lambda
  -> Fixed simulated response
```

Additional local validation path:

```text
Local Python invocation
  -> backend.handler.lambda_handler
  -> Fixed JSON response
```

Current notes:

- The frontend runs locally only.
- The backend runs in AWS Lambda.
- The frontend sends a real `POST` request to the deployed Function URL.
- The backend validates the request and returns a fixed JSON answer.
- Amazon Bedrock is not integrated yet.
- CORS for deployed browser requests is handled by the Function URL layer.
- The Lambda response body keeps only its JSON content header to avoid duplicate CORS headers in browser traffic.

## Current Components

### Frontend

- Plain HTML, CSS, and JavaScript in `frontend/`
- Reads backend configuration from `frontend/config.js`
- Uses `fetch` plus `AbortController`
- Renders success and error states without `innerHTML`

### Public backend entry point

- AWS Lambda Function URL
- Public and unauthenticated in this educational phase
- CORS currently permissive for local browser testing

### Lambda backend

- Python handler in `backend.handler`
- Shared validation and response helpers
- Fixed response to preserve scope before Bedrock integration

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
    "code": "INVALID_REQUEST",
    "message": "..."
  }
}
```

Detailed contract: [docs/api.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/api.md)

## Future Planned Architecture

Status: planned only.

```text
S3-hosted frontend
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
  -> AWS Lambda
  -> Frontend response
```

## Planned Responsibilities

### Frontend

- Render the question-and-answer interface
- Submit a question to the backend over HTTPS
- Render the backend response and error states

### Lambda backend

- Validate incoming questions
- Call Amazon Bedrock in a later phase
- Return a stable JSON contract to the frontend

### Amazon Bedrock

- Provide model inference for user questions
- Remain abstracted behind backend code so model choice can evolve later

## Planned Deployment Flow

```text
Feature branch
  -> Pull Request
  -> CI validation
  -> Merge to main
  -> GitHub Actions
  -> AWS SAM backend deployment
  -> S3 frontend synchronization
```

Status: planned only. CI/CD and S3 frontend deployment do not exist yet.
