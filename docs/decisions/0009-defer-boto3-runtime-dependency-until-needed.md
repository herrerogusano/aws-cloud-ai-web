# ADR 0009: Defer boto3 Runtime Dependency Until Needed

## Status

Accepted

## Context

The backend will run on AWS Lambda. Python Lambda runtimes commonly include the AWS SDK, so adding `boto3` immediately would introduce a runtime dependency before the application code proves it is necessary.

## Decision

Do not add `boto3` as a project runtime dependency during the foundation phase.

## Alternatives Considered

- Add `boto3` immediately as a runtime dependency

## Consequences

- The initial runtime dependency list stays empty.
- Bedrock integration work must confirm whether the managed runtime SDK version is sufficient.
- If explicit SDK pinning becomes necessary later, the dependency strategy should be updated deliberately.
