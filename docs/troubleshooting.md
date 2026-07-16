# Troubleshooting

This guide collects the most likely problems for `aws-cloud-ai-web` and the first practical checks to run.

## Bedrock Access Denied

Symptoms:

- Lambda returns a controlled `LLM_ERROR`
- CloudWatch logs show a provider failure category related to access

Checks:

- Confirm the Lambda execution role still has Bedrock permissions
- Confirm the selected model profile is still `eu.amazon.nova-micro-v1:0`
- Confirm the AWS account still has access to the chosen model profile in `eu-west-1`

## Wrong Model ID or Unavailable Model

Symptoms:

- Lambda returns a controlled `LLM_ERROR`
- Logs indicate `model_unavailable`

Checks:

- Confirm `BEDROCK_MODEL_ID` in `template.yaml`
- Confirm the model or inference profile exists in `eu-west-1`
- Confirm the account has access to it

## Lambda Timeout

Symptoms:

- Frontend shows a timeout message
- Lambda logs show duration close to timeout

Checks:

- Confirm Bedrock latency in CloudWatch logs
- Confirm Lambda timeout is still `20`
- Confirm frontend timeout is still above the Lambda timeout

## CORS Failure

Symptoms:

- Browser blocks requests from the public site or localhost

Checks:

- Confirm Function URL CORS origins include:
  - `http://localhost:8000`
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`
- Confirm the frontend is calling the real Function URL
- Confirm the browser request is `POST` with `Content-Type: application/json`

## Function URL Permission or Method Failure

Symptoms:

- Requests fail unexpectedly

Checks:

- Send `GET` to the Function URL
- Confirm the service returns controlled `405 METHOD_NOT_ALLOWED`
- If that fails, inspect stack status and Function URL configuration

## S3 Public Access Failure

Symptoms:

- Website URL returns `403`
- HTML loads partially or assets are missing

Checks:

- Confirm website hosting is enabled on the bucket
- Confirm the bucket policy still allows public `s3:GetObject`
- Confirm the bucket public access block matches the intended public-read setup

## Wrong `aws s3 sync` Target

Symptoms:

- Frontend files disappear or unexpected files are replaced

Checks:

- Confirm `AWS_FRONTEND_BUCKET` is `aws-cloud-ai-web-herrerogusano-frontend`
- Confirm the sync source is `frontend/`
- Be careful with `--delete`

## OIDC Trust Mismatch

Symptoms:

- GitHub Actions cannot assume the deployment role

Checks:

- Confirm workflow permissions include `id-token: write`
- Confirm trust audience is `sts.amazonaws.com`
- Confirm trust subject is `repo:herrerogusano/aws-cloud-ai-web:ref:refs/heads/main`
- Confirm the workflow is running from `main` when using the production roles

## `iam:PassRole` Failure

Symptoms:

- `sam deploy` fails during GitHub Actions or manual role-based deployment

Checks:

- Confirm the GitHub backend deploy role can pass only the CloudFormation execution role
- Confirm the CloudFormation execution role can pass the Lambda execution role to `lambda.amazonaws.com`

## CloudFormation Rollback

Symptoms:

- Stack update enters rollback or fails to update

Checks:

- Inspect stack events:

```bash
aws cloudformation describe-stack-events --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

- Confirm the execution role still covers Lambda, logs, bucket infrastructure, and the stack-managed IAM role

## `sam deploy` S3 Resolution Conflict

Symptoms:

- Error:
  - `Cannot use both --resolve-s3 and --s3-bucket parameters in non-guided deployments`

Cause:

- `samconfig.toml` enables `resolve_s3 = true`
- the workflow also provides an explicit artifact bucket

Fix:

- In automation, use `--no-resolve-s3` together with `--s3-bucket`
- For local manual deploys, continue using `--resolve-s3` if that is your intended mode

## Windows `sam build` Access Error

Symptoms:

- `sam build` fails while removing `.aws-sam/build`

Likely cause:

- A stale or locked build directory on Windows

Fix:

```powershell
Remove-Item -LiteralPath '.aws-sam\build' -Recurse -Force
sam build
```

## Stale Browser Cache

Symptoms:

- Website loads but old text or old JavaScript behavior remains

Checks:

- Hard refresh the browser
- Retry with a cache-busting query string
- Confirm the workflow re-uploaded `index.html` and `config.js` with `no-cache` headers
