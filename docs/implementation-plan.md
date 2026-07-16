# Implementation Plan and Final Status

This document records the project phases, what was verified, and what remains before the repository can be treated as fully closed.

## Project Objective

Build a small portfolio application where a user submits a question in a browser, the frontend sends it to AWS Lambda, and the backend returns a real answer generated through Amazon Bedrock.

## Final Architecture

```text
Browser
  -> Amazon S3 static website
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
```

## Validation Strategy

- Local quality checks with `uv`, Ruff, mypy, pytest, `sam validate`, and `sam build`
- Manual or controlled smoke checks for deployed infrastructure
- Minimal direct Bedrock validation to avoid unnecessary paid requests
- GitHub Actions CI for Pull Requests
- GitHub Actions CD for pushes to `main`

## Phase Status

### 1. Project foundation

- Status: complete

### 2. Local frontend

- Status: complete

### 3. Local Lambda handler

- Status: complete

### 4. SAM backend deployment

- Status: complete

### 5. Frontend and backend integration

- Status: complete

### 6. Bedrock integration

- Status: complete
- Model profile selected: `eu.amazon.nova-micro-v1:0`
- API style: Converse API

### 7. S3 frontend deployment

- Status: complete
- Public website URL:
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`

### 8. Pull Request CI

- Status: complete
- Verified real CI run on July 16, 2026:
  - GitHub Actions run `29526089317`

### 9. Automatic production deployment

- Status: not yet reverified after fix
- What is verified:
  - Frontend-only production deployment succeeded on July 16, 2026
  - The full backend-plus-frontend workflow structure exists
  - The latest merged run on `main` failed because `sam deploy` received both `resolve_s3` and `--s3-bucket`
- Fix prepared on branch:
  - `docs/project-closure` adds `--no-resolve-s3` to `.github/workflows/deploy.yml`
- What remains:
  - merge the branch
  - confirm a successful `Deploy Production` run on `main`

### 10. Portfolio closure

- Status: prepared in branch, pending merge of the closure PR
- Completed in this phase:
  - README rewrite
  - architecture documentation rewrite
  - deployment documentation completion
  - teardown documentation completion
  - security review
  - cost review
  - troubleshooting guide
  - demo script
  - interview notes
  - lessons learned
  - vault update preparation

## Final Validation Performed on July 16, 2026

Local commands:

- `uv sync --frozen`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy .`
- `uv run pytest`
- `sam validate`
- `sam build`

Observed results:

- Local quality checks passed
- `sam build` passed after cleaning a stale `.aws-sam/build` directory on Windows
- Backend smoke check passed against the deployed Function URL
- Frontend smoke check passed against the public S3 website
- One direct `POST` request produced a real Bedrock answer
- CloudWatch logs showed request start, Bedrock start, Bedrock completion, request completion, and duration without logging the full prompt or answer

## Current Known Limitations

- The public website remains HTTP because S3 static website hosting is being used without CloudFront
- The backend entry point is public and unauthenticated
- There is no rate limiting
- There is no production-grade abuse protection
- The production deployment workflow fix still needs one merged run on `main` to be fully reverified

## Exact Recommended Next Step

1. Merge the `docs/project-closure` Pull Request into `main`.
2. Confirm the next `Deploy Production` workflow run succeeds on `main`.
3. If that succeeds, mark automatic production deployment and portfolio closure as fully complete.
