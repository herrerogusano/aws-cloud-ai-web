# Local API Contract

This document describes the current local Lambda handler contract for Phase 3.

Status: implemented locally only. No AWS deployment exists yet.

## Endpoint Shape

Planned entry point:

- Handler: `backend.handler.lambda_handler`
- Method: `POST`
- Path: `/`

The frontend is not connected to this handler yet.

## Request Body

Expected JSON body:

```json
{
  "question": "¿Qué es AWS Lambda?"
}
```

## Validation Rules

The `question` field must:

- exist
- be a string
- be trimmed
- not be empty
- not exceed 1000 characters

## Successful Response

Example response:

```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
    "Content-Type": "application/json"
  },
  "body": "{\"answer\":\"Esta es una respuesta simulada del backend para la pregunta: «¿Qué es AWS Lambda?». La integración con Amazon Bedrock se añadirá en una fase posterior.\"}"
}
```

The response body always contains JSON.

## Error Response Shape

Every error uses this structure:

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
- `INTERNAL_ERROR`

## Status Codes

- `200` for successful requests
- `400` for malformed JSON or invalid request content
- `405` for unsupported HTTP methods
- `500` for unexpected internal errors

## Event Compatibility Notes

- Production-compatible string bodies are supported
- Dictionary bodies are also accepted for local test convenience
- Missing HTTP methods are treated as `POST` for local compatibility
- Base64-encoded request bodies are rejected in this phase
