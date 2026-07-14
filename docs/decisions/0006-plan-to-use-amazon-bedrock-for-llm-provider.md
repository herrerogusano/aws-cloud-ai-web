# ADR 0006: Plan To Use Amazon Bedrock For The LLM Provider

## Status

Accepted

## Context

The project goal is to demonstrate an AWS-native portfolio application that can call a managed LLM service from Lambda.

## Decision

Plan to use Amazon Bedrock as the LLM provider.

## Alternatives Considered

- Calling a non-AWS LLM API directly
- Building the project without LLM integration

## Consequences

- The backend design must allow later integration with the Bedrock runtime APIs.
- Bedrock model access and model selection remain future implementation concerns.
- This ADR does not claim that Bedrock model access or specific model availability has already been verified.
