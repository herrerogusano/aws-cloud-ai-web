# ADR 0001: Use Python For The Backend

## Status

Accepted

## Context

The project needs a backend language suitable for AWS Lambda, quick iteration, straightforward testing, and readable portfolio code.

## Decision

Use Python for the backend implementation.

## Alternatives Considered

- Node.js
- TypeScript
- Go

## Consequences

- The local toolchain will center on Python-based development tools.
- The Lambda runtime will later need to align with the selected Python version.
- Backend tests and static analysis can be handled with mature Python tooling.
