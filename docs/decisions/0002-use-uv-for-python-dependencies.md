# ADR 0002: Use uv For Python Dependencies

## Status

Accepted

## Context

The project needs Python dependency management that is fast, reproducible, and simple to use from local development and CI.

## Decision

Use `uv` for dependency management and environment synchronization.

## Alternatives Considered

- `pip` with manual virtual environment management
- Poetry
- Pipenv

## Consequences

- The project will use `uv sync` as the default environment setup command.
- The lockfile becomes part of the reproducible toolchain setup.
- Developer onboarding remains focused on a single Python-native tool.
