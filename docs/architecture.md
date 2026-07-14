# Planned Architecture

This document describes the intended architecture for `aws-cloud-ai-web`.

Status: planned only. Nothing described here has been deployed yet.

## Current Local Frontend Architecture

This is the only implemented architecture as of Phase 2:

```text
User
  -> Local static HTML page
  -> Plain JavaScript form handling
  -> Simulated in-browser response
```

No backend call, AWS resource, or network integration exists yet.

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

This contract is intentionally provisional until backend implementation starts.

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
