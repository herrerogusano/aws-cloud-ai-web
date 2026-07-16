# Security Review

This review documents the practical security posture of `aws-cloud-ai-web` for its educational scope.

Review date:

- July 16, 2026

## Scope

- Repository contents
- Frontend static assets
- Lambda backend behavior
- IAM roles
- GitHub OIDC deployment path
- Public AWS surfaces

## Repository Review

Checks performed:

- Searched the repository for common credential patterns
- Reviewed static frontend configuration
- Reviewed workflow configuration
- Reviewed Lambda error behavior

Result:

- No obvious AWS access keys, private keys, tokens, or `.env` secrets were found in the working tree
- The frontend contains a public Function URL in `frontend/config.js`, which is configuration, not a secret
- The workflows use OIDC and do not store permanent AWS deployment keys in GitHub

## Frontend Review

Findings:

- The frontend is intentionally public and should contain only public assets
- User-visible answer rendering uses safe text rendering instead of `innerHTML`
- Frontend errors remain user-oriented and do not expose raw backend internals
- No secret values are shipped in static files

Residual limitations:

- The public website is HTTP, not HTTPS
- Anyone can inspect the frontend assets and the public backend URL

## Backend Review

Verified behavior:

- Accepts only `POST`
- Validates JSON structure and question length
- Maps provider failures to controlled public errors
- Does not return raw Bedrock payloads
- Logs request ID, event type, model ID, and duration
- Does not log the full question or the full answer by default

Residual limitations:

- The Function URL is public and unauthenticated
- There is no rate limiting
- There is no abuse protection such as WAF or CAPTCHA

## IAM Review

### Lambda execution role

Observed intent:

- Basic Lambda logging
- Scoped Bedrock access through inference profile and related model permissions

Positive findings:

- No broad Bedrock managed policy such as `AmazonBedrockFullAccess`
- Bedrock access is attached to the runtime role instead of an application secret

### GitHub backend deploy role

Observed intent:

- CloudFormation orchestration for the existing stack
- SAM artifact upload
- `iam:PassRole` only to the CloudFormation execution role

Positive findings:

- Trust restricted to the repository and branch `main`
- No attached administrator policy

### CloudFormation execution role

Observed intent:

- Scoped mutation of the stack-managed Lambda, Function URL, log group, frontend bucket infrastructure, and Lambda execution role

Positive findings:

- Trust restricted to `cloudformation.amazonaws.com`
- No permission to modify the GitHub OIDC provider or GitHub deployment roles

### GitHub frontend deploy role

Observed intent:

- S3 sync operations limited to the frontend bucket

Positive findings:

- Trust restricted to the repository and branch `main`
- No backend deployment permission
- No attached administrator policy

## OIDC Review

Verified:

- GitHub Actions uses OIDC federation
- Trust policy audience is `sts.amazonaws.com`
- Trust policy subject is restricted to `repo:herrerogusano/aws-cloud-ai-web:ref:refs/heads/main`

Positive outcome:

- No permanent AWS access keys are needed in GitHub Actions for deployment

## Public AWS Surface Review

### S3 website bucket

- Public: yes
- Intended: yes
- Public write: no
- Risk:
  - every uploaded file is public by design

### Lambda Function URL

- Public: yes
- Intended: yes for this project phase
- Auth type: `NONE`
- Risk:
  - any user can attempt requests directly

### CloudWatch logs

- Public: no
- Retention: 7 days
- Risk:
  - operational logs still need discipline, but current logging does not include full prompts or full answers

## Security Findings Summary

No leaked secret was found during repository review.

Main accepted limitations:

1. Public unauthenticated backend
2. HTTP-only public frontend
3. No rate limiting or abuse protection

These are acceptable for a portfolio exercise but would not be sufficient for a production internet-facing application.
