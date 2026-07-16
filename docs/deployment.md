# Deployment Notes

Status: frontend and backend deployed for Phase 7.

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
