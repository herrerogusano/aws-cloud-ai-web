# Deployment Notes

Status: backend deployed for Phase 6. Frontend remains local only.

## Deployed Scope

- Backend: AWS Lambda deployed through AWS SAM
- Public backend endpoint: Lambda Function URL
- Frontend: local only
- Bedrock: integrated through the Converse API

## Current Deployment Values

- Stack name: `aws-cloud-ai-web-backend`
- Region: `eu-west-1`
- Function name: `aws-cloud-ai-web-backend-handler`
- Function URL: `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`
- Bedrock model profile: `eu.amazon.nova-micro-v1:0`

## Bedrock Prerequisites

Before deploying Bedrock-backed changes:

- verify target region availability for the model or inference profile
- verify the current AWS account can invoke the selected model
- verify whether the model requires direct model invocation or an inference profile
- verify expected pricing or credit consumption
- confirm that any required model access or subscription step has already been handled by the user

For this phase, those checks were completed before deployment and the selected profile was successfully invoked from the current AWS account in `eu-west-1`.

## Local Frontend Configuration

The local frontend reads its backend URL from `frontend/config.js`.

Current configuration decision:

- `config.js` is committed in this phase because the Function URL is already public and not a secret
- `config.example.js` is the safe template for future environment changes
- the URL should still be treated as environment-specific configuration

Run the local frontend with:

```bash
python -m http.server 8000 --directory frontend
```

Then open:

```text
http://localhost:8000
```

## Prerequisites

- AWS CLI installed locally
- AWS SAM CLI installed locally
- valid AWS credentials
- region configured for `eu-west-1`
- Python tooling already validated locally

## Environment Variables

Configured through `template.yaml`:

```text
BEDROCK_MODEL_ID=eu.amazon.nova-micro-v1:0
BEDROCK_MAX_TOKENS=500
BEDROCK_TEMPERATURE=0.3
```

## IAM

The Lambda execution role requires only:

- `bedrock:GetInferenceProfile`
- `bedrock:InvokeModel`

The deployed template scopes those permissions to:

- the selected inference profile ARN
- the linked `amazon.nova-micro-v1:0` foundation-model ARNs required by that profile

No separate application secrets are needed because Bedrock uses the Lambda IAM role.

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

If Python dependencies change and SAM must include them:

```bash
uv export --format requirements-txt --no-dev --output-file requirements.txt
```

Known local note:

- If `sam build` fails on Windows with access errors in `.aws-sam/build`, remove that directory and rerun the build.

## Retrieving Outputs

```bash
sam list stack-outputs --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

or:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-backend --query "Stacks[0].Outputs"
```

## Deployment Commands

Preview the update first:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-execute-changeset --no-fail-on-empty-changeset
```

Then deploy:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-confirm-changeset --no-fail-on-empty-changeset
```

## Phase 6 Deployment Result

Deployment date:

- July 16, 2026

CloudFormation review showed only:

- `Modify` on `QuestionHandlerFunctionRole`
- `Modify` on `QuestionHandlerFunction`

No new stack was created.

## Smoke Test Commands

Successful request:

```bash
curl -X POST "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is AWS Lambda?"}'
```

Wrong method:

```bash
curl -X GET "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/"
```

## Troubleshooting

If the frontend shows `La aplicacion no tiene configurado el servicio backend.`:

- check `frontend/config.js`
- ensure `window.APP_CONFIG.apiUrl` exists and is a valid `http` or `https` URL

If the frontend shows `No se ha podido conectar con el servicio...`:

- confirm the Function URL is still reachable
- confirm the local page is being served over `http://localhost:8000` or similar
- if backend code or Function URL CORS behavior changed, redeploy the same SAM stack

If the backend returns `LLM_ERROR`:

- inspect CloudWatch logs for `bedrock_invocation_failed`
- confirm the selected model profile is still available in `eu-west-1`
- confirm IAM still allows the selected inference profile and linked foundation-model ARNs
- distinguish temporary failures such as throttling or service unavailability from access or configuration issues

If `sam build` skips dependencies:

- confirm `requirements.txt` exists at the project root used by `CodeUri`
- regenerate it from `uv` after dependency changes

If `sam build` fails on Windows with access errors:

- remove `.aws-sam/build`
- run `sam build` again

## Security Notes

- The Function URL uses `AuthType: NONE`
- Public unauthenticated access is intentional only for this educational phase
- CORS is not authentication
- Bedrock access relies on the Lambda IAM role, not on frontend or environment secrets
