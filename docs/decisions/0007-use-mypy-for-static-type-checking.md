# ADR 0007: Use mypy For Static Type Checking

## Status

Accepted

## Context

The project needs one static type checker. The initial toolchain should stay simple, Python-native, and easy to run through `uv` without adding a Node.js dependency.

## Decision

Use `mypy` for static type checking.

## Alternatives Considered

- Pyright

## Consequences

- The core quality toolchain remains fully Python-based.
- Strict typing rules can be enforced early with minimal extra setup.
- If the project later benefits more from Pyright semantics, this decision can be revisited.
