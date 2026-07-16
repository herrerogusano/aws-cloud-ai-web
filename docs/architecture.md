# Architecture

This document describes the current implemented architecture for `aws-cloud-ai-web`.

## Current Architecture

Status: implemented as of Phase 6 on July 16, 2026.

```text
Local browser frontend
  -> Local static files served over HTTP
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
  -> Generated answer
```

Additional local validation path:

```text
Local Python tests
  -> backend.handler.lambda_handler
  -> mocked Bedrock client
  -> Stable JSON response contract
```

## Current Components

### Frontend

- Plain HTML, CSS, and JavaScript in `frontend/`
- Reads backend configuration from `frontend/config.js`
- Uses `fetch` plus `AbortController`
- Uses a 25-second browser timeout to stay above the 20-second Lambda timeout
- Renders success and error states without `innerHTML`

### Public backend entry point

- AWS Lambda Function URL
- Public and unauthenticated in this educational phase
- CORS currently permissive for local browser testing

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

Current intent of the system instruction:

```text
You are a helpful assistant.
Answer the user's question clearly and concisely.
Do not claim access to information or tools you do not have.
```

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

The Lambda execution role now includes:

- `bedrock:GetInferenceProfile` on the selected inference profile ARN
- `bedrock:InvokeModel` on the selected inference profile ARN
- `bedrock:InvokeModel` on the linked `amazon.nova-micro-v1:0` foundation-model ARNs for the profile regions
- a `bedrock:InferenceProfileArn` condition to keep the foundation-model permission tied to the selected profile

No broad Bedrock managed policy was attached.

## Still Not In Scope

- S3-hosted frontend
- CloudFront
- API Gateway
- authentication
- database storage
- chat history
- CI/CD

## Planned Next Phase

```text
S3-hosted frontend
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
```

Status: planned only for Phase 7.
