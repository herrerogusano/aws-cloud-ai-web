# ADR 0010: Package boto3 With The Lambda For Bedrock Converse Support

## Status

Accepted

## Context

Phase 6 integrates Amazon Bedrock through the Converse API. The project could either rely on the AWS SDK version included in the managed Lambda runtime or package a pinned `boto3` version with the application.

The managed runtime approach would keep the artifact smaller, but it would leave the deployed Bedrock feature coupled to whatever SDK version happened to be present in the runtime. For Bedrock Converse support, that uncertainty is not desirable in a portfolio project where the deployed behavior should stay reproducible.

AWS SAM also does not package Python dependencies directly from `pyproject.toml`, so a pinned dependency strategy must include a manifest that SAM actually consumes.

## Decision

Package `boto3` with the application and export `requirements.txt` from `uv` so AWS SAM includes the pinned SDK in the Lambda artifact.

## Alternatives Considered

- Rely on the AWS SDK bundled with the Lambda Python runtime
- Add `boto3` locally for development only and let the deployed runtime differ

## Consequences

- The deployment artifact is larger than in the runtime-SDK approach
- The Bedrock client behavior is more predictable across local validation and deployment
- Dependency changes now require regenerating `requirements.txt` from `uv`
- ADR 0009 remains historically correct for the foundation phase but is superseded for the Bedrock integration phase
