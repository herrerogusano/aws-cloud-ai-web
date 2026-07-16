# Deployment Notes

Status: backend deployed for Phase 5. Frontend remains local only.

## Deployed Scope

- Backend: AWS Lambda deployed through AWS SAM
- Public backend endpoint: Lambda Function URL
- Frontend: local only
- Bedrock: not integrated

## Current Deployment Values

- Stack name: `aws-cloud-ai-web-backend`
- Region: `eu-west-1`
- Function name: `aws-cloud-ai-web-backend-handler`
- Function URL: `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`

## Local Frontend Configuration

The local frontend reads its backend URL from `frontend/config.js`.

Current configuration decision:

- `config.js` is committed in this phase because the Function URL is already public and not a secret
- `config.example.js` is the safe template for future environment changes
- The URL should still be treated as environment-specific configuration

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

## Deployment Command

The stack is deployed with:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-confirm-changeset --no-fail-on-empty-changeset
```

When reviewing a stack update first:

```bash
sam deploy --stack-name aws-cloud-ai-web-backend --region eu-west-1 --resolve-s3 --capabilities CAPABILITY_IAM --no-execute-changeset --no-fail-on-empty-changeset
```

## Phase 5 Backend Update

During frontend integration, a real browser request revealed duplicate `Access-Control-Allow-Origin` headers on deployed `POST` responses.

Observed behavior:

- `OPTIONS` preflight succeeded
- Browser `fetch` still failed from `http://localhost:8000`
- CLI inspection showed the Function URL layer and the Lambda response were both adding `Access-Control-Allow-Origin`

Resolution:

- Removed CORS headers from Lambda response helpers
- Kept `Content-Type: application/json` in Lambda responses
- Left deployed browser CORS ownership to the Function URL layer
- Redeployed the same stack

CloudFormation review for that update showed only:

- `Modify` on `QuestionHandlerFunction`

No new AWS resources were created.

## Smoke Test Commands

Successful request:

```bash
curl -X POST "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Origin: http://localhost:8000" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is AWS Lambda?"}'
```

Preflight check:

```bash
curl -X OPTIONS "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Origin: http://localhost:8000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

Wrong method:

```bash
curl -X GET "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Origin: http://localhost:8000"
```

## Browser Verification Notes

Confirmed in a real browser flow:

- The local frontend loaded from `http://localhost:8000`
- Empty input validation still worked
- The valid question flow performed a real backend request
- Loading state and disabled submit behavior were visible during the request
- The deployed fixed answer rendered successfully
- CORS worked after the backend redeploy
- A bad Function URL produced the expected connection-error UI

## Common Failures

- `NoCredentials`: configure AWS credentials before deployment
- `AccessDenied` on CloudFormation: expand IAM permissions for the deployment identity
- `sam build` permission errors on Windows: remove `.aws-sam/build` and rerun
- Browser connection error after backend change: inspect for duplicate `Access-Control-Allow-Origin` headers
- `sam local invoke` container errors: ensure Docker is running and reachable

## Security Notes

- The Function URL uses `AuthType: NONE`
- Public unauthenticated access is intentional only for this educational phase
- CORS is not authentication
- Bedrock is not used in this phase
