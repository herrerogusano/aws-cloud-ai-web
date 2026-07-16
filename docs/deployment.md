# Deployment Notes

Status: deployed for Phase 4.

## Deployed Scope

- Backend: AWS Lambda deployed through AWS SAM
- Public backend endpoint: Lambda Function URL
- Frontend: not deployed yet
- Bedrock: not integrated

## Current Deployment Values

- Stack name: `aws-cloud-ai-web-backend`
- Region: `eu-west-1`
- Function name: `aws-cloud-ai-web-backend-handler`
- Function URL: `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`

## Prerequisites

- AWS CLI installed locally
- AWS SAM CLI installed locally
- Valid AWS credentials
- Region configured for `eu-west-1`
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

Notes:

- `sam local invoke` remained blocked in this environment because Docker was not available to SAM even though Docker Desktop was installed.
- This did not block deployment because unit tests, SAM validation, and SAM build all passed.

## Deployment Command

The stack was deployed with:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-confirm-changeset --no-fail-on-empty-changeset
```

The first attempt used `--confirm-changeset`, but that interactive confirmation was not practical in this environment after the changeset preview had already been inspected.

## Retrieving Outputs

```bash
sam list stack-outputs --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

or:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-backend --query "Stacks[0].Outputs"
```

## Smoke Test Commands

Successful request:

```bash
curl -X POST "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Content-Type: application/json" \
  -d '{"question":"Que es AWS Lambda?"}'
```

Validation failure:

```bash
curl -X POST "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Content-Type: application/json" \
  -d '{"question":"   "}'
```

Wrong method:

```bash
curl -X GET "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/"
```

Preflight check:

```bash
curl -X OPTIONS "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Origin: http://localhost:8000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

## Common Failures

- `NoCredentials`: configure AWS credentials before deployment
- `AccessDenied` on CloudFormation: expand IAM permissions for the deployment identity
- `sam build` permission errors on Windows: remove `.aws-sam/build` and rerun
- `sam local invoke` container errors: ensure Docker is running and reachable

## Security Notes

- The Function URL uses `AuthType: NONE`
- Public unauthenticated access is intentional only for this educational phase
- CORS is not authentication
- Bedrock is not used in this phase
