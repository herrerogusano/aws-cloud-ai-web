# Planned Architecture

This document describes the intended architecture for `aws-cloud-ai-web`.

Status: planned only. Nothing described here has been deployed yet.

## Current Architecture

This is the implemented architecture as of Phase 4:

```text
User
  -> Lambda Function URL
  -> AWS Lambda
  -> Fixed simulated response

Local validation
  -> Python Lambda handler
  -> Fixed JSON response
```

The frontend and backend currently exist as separate pieces.

- The backend is deployed in AWS through SAM.
- The frontend remains local and still uses JavaScript-only simulation.
- No frontend-to-backend connection exists yet.

## Current Separate Frontend State

```text
Local static frontend
  -> Local JavaScript simulation
```

## Planned Request Flow

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

## Planned Components

- Static frontend hosted from Amazon S3
- Single AWS Lambda backend entry point
- Public HTTPS access through a Lambda Function URL
- LLM inference through Amazon Bedrock

## Planned Responsibilities

### Frontend

- Render a minimal question-and-answer interface
- Submit a question to the backend over HTTPS
- Render the backend response and basic error states

### Lambda backend

- Accept a validated request payload from the frontend
- Normalize and validate the incoming question
- Call Amazon Bedrock
- Return a stable JSON response contract to the frontend

### Amazon Bedrock

- Provide the model inference capability for user questions
- Remain abstracted behind backend code so model choice can evolve later

## Planned API Shape

The public endpoint is planned as a Lambda Function URL.

Current planned contract:

- Method: `POST`
- Path: `/`
- Request content type: `application/json`
- Request body:

```json
{
  "question": "What can you tell me about serverless architectures?"
}
```

- Planned successful response:

```json
{
  "answer": "..."
}
```

- Planned validation error response:

```json
{
  "error": "question is required"
}
```

Current local backend implementation already follows the same general response shape:

- `POST` requests only
- JSON request body with `question`
- JSON response body with `answer`
- JSON error bodies with status codes

Detailed local contract: [docs/api.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/api.md)

## Next Integration Step

```text
Local frontend
  -> Deployed Lambda Function URL
```

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

Status: planned only. CI/CD has not been implemented yet.

## Security Principles

- Keep public access limited to the intended HTTPS entry point
- Validate request payloads before invoking Amazon Bedrock
- Avoid storing secrets in the repository
- Prefer least-privilege IAM when infrastructure is introduced later
- Keep user-facing errors generic and log detail server-side only

## Cost Principles

- Keep the architecture intentionally small
- Avoid unnecessary always-on infrastructure
- Delay Bedrock and deployment setup until implementation requires them
- Add cost awareness checks before enabling automated deployment
