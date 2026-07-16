# Deployment Notes

Status: frontend and backend are deployed, and the repository is prepared for GitHub Actions PR validation plus frontend-only deployment to S3.

## Deployed Scope

- Frontend: S3 static website
- Backend: AWS Lambda deployed through AWS SAM
- Public backend endpoint: Lambda Function URL
- Bedrock: integrated through the Converse API

## Current Deployment Values

- Stack name: `aws-cloud-ai-web-backend`
- Region: `eu-west-1`
- Function name: `aws-cloud-ai-web-backend-handler`
- Function URL: `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`
- Frontend bucket name: `aws-cloud-ai-web-herrerogusano-frontend`
- Frontend website URL: `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`
- Bedrock model profile: `eu.amazon.nova-micro-v1:0`

## Frontend Build Requirements

- none

The frontend is plain static HTML, CSS, and JavaScript and does not require a build step before upload.

## Frontend Configuration

The deployed frontend reads its backend URL from `frontend/config.js`.

Current configuration decision:

- `config.js` is committed with the public Function URL
- the URL is not treated as a secret
- `config.example.js` remains as a local template only
- `config.example.js` is excluded from S3 sync

## CORS

The Function URL CORS configuration currently allows:

- `http://localhost:8000`
- `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`

This keeps local development working while allowing the public S3 website origin.

## S3 Hosting Notes

The frontend uses S3 static website hosting, which means:

- the public website endpoint is `HTTP`
- the backend remains `HTTPS`
- browser requests from the HTTP S3 site to the HTTPS Function URL were verified successfully in a real browser

Do not claim this is an ideal final production architecture.

A future improvement could add CloudFront for HTTPS, but that is intentionally out of scope in this phase.

## Prerequisites

- AWS CLI installed locally
- AWS SAM CLI installed locally
- valid AWS credentials
- region configured for `eu-west-1`
- Python tooling already validated locally
- GitHub repository admin access for variables and workflow review

## Local Validation Before Deployment

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run mypy .
sam validate
sam build
```

Known local note:

- If `sam build` fails on Windows with access errors in `.aws-sam` directories, remove that directory and rerun the build.

## Retrieving Outputs

```bash
sam list stack-outputs --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

or:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-backend --query "Stacks[0].Outputs"
```

## Infrastructure Deployment

Preview the update first:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-execute-changeset --no-fail-on-empty-changeset
```

Then deploy:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-confirm-changeset --no-fail-on-empty-changeset
```

## Frontend Asset Synchronization

Use the project helper script:

```bash
powershell -ExecutionPolicy Bypass -File scripts/sync_frontend.ps1 -BucketName aws-cloud-ai-web-herrerogusano-frontend
```

The script uses `aws s3 sync frontend/ ... --delete` and excludes:

- `config.example.js`
- `.env`
- `.env.*`
- `*.map`
- `.DS_Store`
- `Thumbs.db`

Before using `--delete`, confirm the target bucket is the project frontend bucket and does not contain unrelated files.

## GitHub Actions CI

Pull Request validation is defined in `.github/workflows/ci.yml`.

Trigger:

- `pull_request` targeting `main`
- `workflow_dispatch`

Permissions:

- `contents: read`

Validation steps:

- `uv sync --frozen`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy .`
- `uv run pytest`
- `sam validate`
- `sam build`

This workflow does not use AWS credentials, does not request OIDC tokens, and does not deploy infrastructure.

## GitHub Actions Frontend Deployment

Frontend deployment is defined in `.github/workflows/deploy-frontend.yml`.

Trigger:

- `push` to `main`
- `workflow_dispatch`

Concurrency:

- `production-frontend`
- `cancel-in-progress: false`

Validation-before-deploy behavior:

- reruns the same quality checks as CI
- fails before authentication if repository variables are missing
- keeps backend deployment out of scope

Deployment command:

```bash
aws s3 sync frontend/ s3://$AWS_FRONTEND_BUCKET --delete
```

Deployment exclusions:

- `config.example.js`
- `.env`
- `.env.*`
- `*.map`
- `.DS_Store`
- `Thumbs.db`

Cache behavior:

- `index.html` is re-uploaded with `Cache-Control: no-cache, no-store, must-revalidate`
- `config.js` is re-uploaded with `Cache-Control: no-cache, no-store, must-revalidate`
- other static assets keep the default S3 sync behavior because filenames are not hashed yet

Smoke check behavior:

- confirm `index.html`, `styles.css`, `app.js`, and `config.js` exist in S3
- request the website URL over HTTP
- confirm the page title and required static assets load
- do not submit an AI question automatically, so the workflow avoids extra Bedrock calls

## GitHub OIDC Bootstrap

Bootstrap IAM is kept separate from the application stack in:

- `bootstrap/github-frontend-deploy-iam.yaml`

Bootstrap scope:

- create or reuse the account-level GitHub OIDC provider for `https://token.actions.githubusercontent.com`
- create the repository-specific role `aws-cloud-ai-web-github-frontend-deploy`
- restrict trust to `repo:herrerogusano/aws-cloud-ai-web:ref:refs/heads/main`
- grant only `s3:ListBucket`, `s3:GetBucketLocation`, `s3:PutObject`, and `s3:DeleteObject` on the frontend bucket

Apply the bootstrap template manually with an administrative AWS identity. Do not run IAM bootstrap from the GitHub deployment workflow itself.

## Required GitHub Repository Variables

- `AWS_REGION=eu-west-1`
- `AWS_FRONTEND_BUCKET=aws-cloud-ai-web-herrerogusano-frontend`
- `AWS_DEPLOY_ROLE_ARN=<GitHub OIDC deployment role ARN>`

These values are configuration, not permanent credentials. Do not store `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` in GitHub for this project.

## Phase 7 Deployment Result

Deployment date:

- July 16, 2026

CloudFormation review showed:

- `Add` on `FrontendWebsiteBucket`
- `Add` on `FrontendWebsiteBucketPolicy`
- `Modify` on `QuestionHandlerFunctionUrl`
- `Modify` on `QuestionHandlerFunction`

No new stack was created.

## Browser Validation Checklist

Validated successfully in this phase:

- the public S3 website loaded
- CSS and JavaScript loaded correctly
- the page submitted a valid question
- the request reached the Lambda
- Bedrock generated the answer
- the answer rendered correctly
- loading state worked
- CORS succeeded
- no mixed-content error appeared
- no unexpected browser console errors appeared
- mobile-width layout collapsed to a single column correctly

## Common S3 Website Errors

- `403 Forbidden` on the website endpoint:
  - confirm the bucket policy allows `s3:GetObject`
  - confirm website hosting is enabled on the bucket
- missing CSS or JavaScript:
  - confirm the sync completed
  - confirm the files are present in the bucket
- website serves old copy:
  - refresh with a cache-busting query string or clear browser cache during validation

## Common OIDC And Workflow Errors

- `Could not assume role with OIDC`:
  - confirm the IAM role trust policy uses `sts.amazonaws.com` as the audience
  - confirm the `sub` claim is restricted to `repo:herrerogusano/aws-cloud-ai-web:ref:refs/heads/main`
  - confirm the workflow has `permissions: id-token: write`
- missing repository variable failure:
  - configure `AWS_REGION`, `AWS_FRONTEND_BUCKET`, and `AWS_DEPLOY_ROLE_ARN`
- S3 permission failure:
  - confirm the deployment role points to the correct bucket
  - confirm the role has bucket-level and object-level permissions for that bucket only
- wrong bucket deployment:
  - confirm the configured bucket is the project website bucket before rerunning a deployment

## Common Public-Access Errors

- public website does not load:
  - check bucket policy
  - check Public Access Block configuration
  - ensure only the bucket policy is used for public reads, not ACLs

## Common CORS Errors

- browser request blocked from S3:
  - confirm the Function URL `AllowOrigins` list contains the exact website origin
  - confirm localhost-only assumptions have been removed
  - verify with an `OPTIONS` preflight request

## Security Notes

- the website bucket is public-read by design
- every object uploaded to that bucket should be considered public
- public write is not allowed
- the Function URL uses `AuthType: NONE`
- CORS is not authentication
- the backend is still deployed manually through AWS SAM in this phase
