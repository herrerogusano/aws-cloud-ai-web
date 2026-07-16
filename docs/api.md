# API Contract

This document describes the current request and response contract between the deployed frontend and the deployed backend.

Status: implemented for Phase 6.

## Public Endpoint

- Entry point: Lambda Function URL
- Region: `eu-west-1`
- Method: `POST`
- Path: `/`
- Request content type: `application/json`

The public frontend and the local development frontend are connected to this deployed endpoint.

## Request Body

Expected JSON body:

```json
{
  "question": "What is AWS Lambda?"
}
```

Rules:

- `question` must exist
- `question` must be a string
- `question` is trimmed before sending
- `question` must not be empty after trimming
- `question` must not exceed 1000 characters

## Successful Response

Expected response body:

```json
{
  "answer": "Generated answer..."
}
```

Notes:

- the response body is JSON
- the frontend expects `answer` to be a string
- the frontend renders the answer with safe text rendering only
- the backend does not expose raw Bedrock payloads

## Error Response Shape

Every backend error uses this structure:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "La pregunta es obligatoria."
  }
}
```

## Error Codes

- `INVALID_JSON`
- `INVALID_REQUEST`
- `QUESTION_TOO_LONG`
- `METHOD_NOT_ALLOWED`
- `LLM_ERROR`
- `INTERNAL_ERROR`

## Status Codes

- `200` for successful requests
- `400` for malformed JSON or invalid request content
- `405` for unsupported HTTP methods
- `502` for provider failure or invalid Bedrock response
- `503` for temporary provider unavailability such as throttling
- `500` for unexpected internal errors

## Browser CORS Behavior

Deployed browser traffic relies on the Lambda Function URL CORS configuration.

Current deployed behavior:

- preflight `OPTIONS` replies from the Function URL layer
- browser `POST` responses include `Access-Control-Allow-Origin` from the Function URL layer
- Lambda response helpers keep only `Content-Type: application/json` to avoid duplicate CORS headers

## Local Handler Invocation Notes

Direct local invocation of `backend.handler.lambda_handler` returns a Lambda-style object:

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"answer\":\"...\"}"
}
```

Local compatibility behavior:

- production-style string bodies are supported
- dictionary bodies are also accepted for local test convenience
- missing HTTP methods are treated as `POST` for local compatibility
- base64-encoded request bodies are rejected in this phase
