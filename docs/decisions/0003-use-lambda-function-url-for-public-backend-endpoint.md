# ADR 0003: Use Lambda Function URL For The Public Backend Endpoint

## Status

Accepted

## Context

The project needs a simple public HTTPS endpoint for a single Lambda-backed portfolio application. The intended scope does not currently require API Gateway features such as advanced routing, authorizers, or usage plans.

## Decision

Use a Lambda Function URL as the planned public backend endpoint.

## Alternatives Considered

- Amazon API Gateway HTTP API
- Amazon API Gateway REST API

## Consequences

- The public entry point remains simple and low-overhead.
- The project should explicitly handle request validation and CORS behavior in the Lambda implementation later.
- If the project scope grows, API Gateway can be reconsidered in a future ADR.
