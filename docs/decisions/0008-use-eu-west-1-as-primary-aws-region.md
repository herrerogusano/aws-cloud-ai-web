# ADR 0008: Use eu-west-1 As The Primary AWS Region

## Status

Accepted

## Context

The project needs one explicit AWS region for future infrastructure, documentation, and deployment commands.

## Decision

Use `eu-west-1` as the primary AWS region.

## Alternatives Considered

- Deferring region selection entirely
- Choosing a different AWS region

## Consequences

- Documentation and future commands can reference one stable target region.
- Any future service availability checks should start with `eu-west-1`.
- If a required service or model constraint appears later, the region choice can be revisited explicitly.
