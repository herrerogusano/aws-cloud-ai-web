# ADR 0004: Use AWS SAM For Infrastructure As Code

## Status

Accepted

## Context

The project needs infrastructure as code that fits a small serverless application and supports Lambda-focused development without unnecessary complexity.

## Decision

Use AWS SAM for infrastructure as code.

## Alternatives Considered

- Raw CloudFormation
- Terraform
- AWS CDK

## Consequences

- Infrastructure definitions will be centered on `template.yaml`.
- Local template validation can use SAM CLI when available.
- The project keeps a narrow serverless-focused infrastructure surface.
