# Deployment

This document explains how to validate, deploy, troubleshoot, and recover `aws-cloud-ai-web`.

## Current Deployment Scope

- Region: `eu-west-1`
- Stack: `aws-cloud-ai-web-backend`
- Public frontend bucket: `aws-cloud-ai-web-herrerogusano-frontend`
- Public website URL: `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`
- Public backend URL: `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`
- Bedrock model profile: `eu.amazon.nova-micro-v1:0`

## Local Prerequisites

- Git
- Python 3.13
- `uv`
- AWS CLI
- AWS SAM CLI
- Docker only if you later need local Lambda container workflows
- Valid AWS credentials for manual deployment

Optional but useful:

- `gh` CLI for reviewing CI/CD runs and Pull Requests

## Local Validation Before Deployment

Run the full suite:

```bash
uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
sam validate
sam build
```

Windows note:

- If `sam build` fails with an access error while removing `.aws-sam/build`, delete that directory and rerun the command.

## Manual Backend Deployment

Preview the change set first:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-execute-changeset --no-fail-on-empty-changeset
```

Apply the deployment:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-confirm-changeset --no-fail-on-empty-changeset
```

Why `CAPABILITY_IAM` is required:

- The stack manages the Lambda execution role.

Retrieve outputs after deployment:

```bash
sam list stack-outputs --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

## Manual Frontend Deployment

Sync the public frontend assets:

```bash
powershell -ExecutionPolicy Bypass -File scripts/sync_frontend.ps1 -BucketName aws-cloud-ai-web-herrerogusano-frontend
```

The sync helper excludes:

- `config.example.js`
- `.env`
- `.env.*`
- `*.map`
- `.DS_Store`
- `Thumbs.db`

Before using `--delete`, confirm the bucket really is the project frontend bucket and contains no unrelated files.

## Automated Deployment

### Pull Request CI

Workflow file:

- `.github/workflows/ci.yml`

Trigger:

- Pull Requests to `main`

Permissions:

- `contents: read`

Checks:

- `uv sync --frozen`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy .`
- `uv run pytest`
- `sam validate`
- `sam build`

Important behavior:

- No AWS deployment credentials
- No OIDC token
- No Bedrock calls
- No infrastructure changes

### Production Deployment

Workflow file:

- `.github/workflows/deploy.yml`

Triggers:

- Push to `main`
- `workflow_dispatch`

Permissions:

- `contents: read`
- `id-token: write`

Concurrency:

- `production-deployment`
- `cancel-in-progress: false`

Deployment order:

1. Validate repository variables.
2. Run the same quality checks used in CI.
3. Assume the GitHub backend deployment role through OIDC.
4. Confirm the target stack and SAM artifact bucket.
5. Run `sam deploy`.
6. Read stack outputs.
7. Run the backend smoke check without invoking Bedrock.
8. Assume the GitHub frontend deployment role.
9. Sync `frontend/` to the S3 website bucket.
10. Reapply no-cache headers to `index.html` and `config.js`.
11. Run the website smoke check.

Backend deployment command:

```bash
sam deploy \
  --stack-name "$SAM_STACK_NAME" \
  --region "$AWS_REGION" \
  --no-resolve-s3 \
  --s3-bucket "$SAM_ARTIFACT_BUCKET" \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset \
  --role-arn "$AWS_CLOUDFORMATION_EXECUTION_ROLE_ARN"
```

Why `--no-resolve-s3` is present:

- `samconfig.toml` keeps `resolve_s3 = true` for local manual deploys.
- The GitHub workflow already uses an explicit artifact bucket through `SAM_ARTIFACT_BUCKET`.
- Without `--no-resolve-s3`, `sam deploy` rejects the command because both modes are set.

Frontend deployment command:

```bash
aws s3 sync frontend/ s3://$AWS_FRONTEND_BUCKET --delete
```

### Required GitHub Repository Variables

- `AWS_REGION=eu-west-1`
- `AWS_BACKEND_DEPLOY_ROLE_ARN=<backend OIDC role ARN>`
- `AWS_CLOUDFORMATION_EXECUTION_ROLE_ARN=<CloudFormation execution role ARN>`
- `AWS_FRONTEND_DEPLOY_ROLE_ARN=<frontend OIDC role ARN>`
- `AWS_FRONTEND_BUCKET=aws-cloud-ai-web-herrerogusano-frontend`
- `SAM_ARTIFACT_BUCKET=aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f`
- `SAM_STACK_NAME=aws-cloud-ai-web-backend`

These are configuration values, not secrets.

## OIDC and IAM Roles

Bootstrap template:

- `bootstrap/github-frontend-deploy-iam.yaml`

Roles:

- `aws-cloud-ai-web-github-backend-deploy`
- `aws-cloud-ai-web-cloudformation-execution`
- `aws-cloud-ai-web-github-frontend-deploy`

Trust restriction used by the GitHub deployment roles:

- `repo:herrerogusano/aws-cloud-ai-web:ref:refs/heads/main`

## Smoke Checks

Backend smoke check:

- Sends `GET` to the Function URL
- Expects `405 METHOD_NOT_ALLOWED`
- Avoids unnecessary Bedrock calls during deployment

Frontend smoke check:

- Requests the public website
- Confirms the HTML loads and references expected assets

## Rollback

Application rollback:

1. Identify the last known good commit.
2. Revert the bad commit or redeploy the older commit through the normal workflow.
3. Merge to `main`.
4. Let GitHub Actions redeploy backend and frontend.

Backend failure:

1. Inspect CloudFormation stack events.
2. Review Lambda logs.
3. Fix the issue and redeploy, or redeploy the last good commit.

Frontend failure:

1. Use a previous known-good commit.
2. Rerun the deployment workflow or manually sync the old frontend files.

## Troubleshooting Summary

For the full guide, see [troubleshooting.md](troubleshooting.md).

Common issues:

- Bedrock access denied
- Wrong model or unavailable model profile
- Lambda timeout
- OIDC trust mismatch
- `iam:PassRole` failure
- CloudFormation rollback
- Wrong S3 sync target
- Browser cache serving stale frontend files
- `sam deploy` conflict between `resolve_s3` and explicit `--s3-bucket`
