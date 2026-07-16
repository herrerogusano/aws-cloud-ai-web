# aws-cloud-ai-web

`aws-cloud-ai-web` is a serverless portfolio project built in phases. The current application is a local static frontend that sends a real question to a deployed AWS Lambda backend through a public Lambda Function URL. The backend still returns a fixed simulated answer for now. Amazon Bedrock is planned for the next implementation phase.

## Current Status

Phase 5 is complete.

- Repository structure and Python tooling are in place.
- The frontend lives in `frontend/` and uses plain HTML, CSS, and JavaScript.
- The backend Lambda is deployed in `eu-west-1` through AWS SAM.
- The frontend now performs a real `POST` request to the deployed Function URL.
- The backend still returns a fixed simulated answer.
- No Amazon Bedrock call exists yet.
- The frontend is not deployed to S3 yet.

## Current Implemented Architecture

```text
Local browser frontend
  -> Lambda Function URL
  -> AWS Lambda
  -> Fixed simulated response
```

Future planned architecture:

```text
S3-hosted frontend
  -> Lambda Function URL
  -> AWS Lambda
  -> Amazon Bedrock
```

More detail: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)

## Technology Choices

- Backend language: Python
- Dependency management: `uv`
- Testing: `pytest`
- Linting and formatting: `Ruff`
- Type checking: `mypy`
- Infrastructure as code: AWS SAM
- Frontend: plain HTML, CSS, and JavaScript
- Public backend endpoint: Lambda Function URL
- Planned LLM provider: Amazon Bedrock
- Planned frontend hosting: Amazon S3
- Planned CI/CD: GitHub Actions
- Git workflow: short-lived branches and Pull Requests
- Commit style: Conventional Commits
- AWS region: `eu-west-1`

## Local Prerequisites

- Python 3.13
- `uv`
- Git
- AWS CLI
- AWS SAM CLI

## Frontend Configuration

The frontend reads the backend URL from `frontend/config.js`.

- `frontend/config.js` is committed in this learning phase because the Function URL is already public and is not a secret.
- `frontend/config.example.js` provides the safe template shape.
- The URL is still treated as environment-specific configuration and should not be scattered through app logic.

Current committed Function URL:

- `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`

Configuration shape:

```javascript
window.APP_CONFIG = {
    apiUrl: "https://example.lambda-url.eu-west-1.on.aws/",
};
```

## Development Commands

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
sam validate
sam build
python -m http.server 8000 --directory frontend
```

Then open `http://localhost:8000`.

To retrieve deployed stack outputs:

```bash
sam list stack-outputs --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

To invoke the backend directly without AWS tooling:

```bash
python -c "from backend.handler import lambda_handler; event={'version':'2.0','requestContext':{'http':{'method':'POST'}},'isBase64Encoded':False,'body':'{\"question\":\"What is AWS Lambda?\"}'}; print(lambda_handler(event, None))"
```

Useful local test fixtures are available in `events/`.

## Current Frontend Functionality

- Accepts one question in a multiline text area
- Rejects empty questions with client-side validation
- Validates the backend URL configuration before sending
- Sends a real `POST` request with `Content-Type: application/json`
- Uses `AbortController` with a 12-second timeout
- Prevents repeated submissions while a request is in progress
- Shows loading, success, and error states
- Renders backend text safely with `textContent`
- Preserves the current question after backend or network errors

## Current Backend Functionality

- Accepts `POST` requests only
- Parses JSON request bodies
- Validates the `question` field with a maximum of 1000 characters
- Returns a fixed JSON answer without Bedrock
- Returns consistent JSON errors with safe public messages
- Relies on the Lambda Function URL CORS configuration for deployed browser access

Important:

- The backend response is still fixed
- No Amazon Bedrock call is made
- No frontend S3 deployment exists yet

## Deployed Backend Endpoint

Current environment-specific Function URL:

- `https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/`

Example request:

```bash
curl -X POST "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is AWS Lambda?"}'
```

Security limitations:

- The Function URL is public and unauthenticated in this phase
- CORS is not authentication or authorization
- This endpoint is acceptable for a learning exercise, not for sensitive production data

## Browser Validation Summary

The frontend was verified against the deployed backend from `http://localhost:8000`.

Confirmed:

- The page loads correctly
- Backend configuration loads from `config.js`
- Empty input is rejected in the browser
- A valid question sends a real request and receives the deployed fixed answer
- The loading state appears and the submit button is disabled during the request
- The browser request succeeds with CORS enabled
- A browser test with an intentionally bad Function URL shows the expected connection error message

Pending:

- A true narrow mobile-width browser pass is still worth checking manually in a normal browser window. The in-app browser viewport override did not actually reduce `window.innerWidth`, so that specific visual confirmation remains weaker than the other checks.

## Troubleshooting

If the frontend shows `La aplicacion no tiene configurado el servicio backend.`:

- Check `frontend/config.js`
- Ensure `window.APP_CONFIG.apiUrl` exists and is a valid `http` or `https` URL

If the frontend shows `No se ha podido conectar con el servicio...`:

- Confirm the Function URL is still reachable
- Confirm the local page is being served over `http://localhost:8000` or similar
- If backend code or Function URL CORS behavior changed, redeploy the same SAM stack
- Do not use `mode: "no-cors"` and do not disable browser security

If browser requests fail after backend updates:

- Check for duplicated `Access-Control-Allow-Origin` headers
- Keep deployed CORS in the Function URL layer and avoid duplicating the same header in Lambda responses

If `sam build` fails on Windows with access errors:

- Remove `.aws-sam/build`
- Run `sam build` again

## Documentation

- Implementation plan: [docs/implementation-plan.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/implementation-plan.md)
- Architecture: [docs/architecture.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/architecture.md)
- API contract: [docs/api.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/api.md)
- Deployment notes: [docs/deployment.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/deployment.md)
- Teardown notes: [docs/teardown.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/teardown.md)
- Resource inventory: [docs/aws-resources.md](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/aws-resources.md)
- Architecture Decision Records: [docs/decisions](/C:/Users/herre/OneDrive/Documentos/aws-cloud-ai-web/docs/decisions)

## Next Planned Phase

The exact recommended next step is Phase 6 from the implementation plan: integrate Amazon Bedrock into the deployed backend while keeping the existing frontend-to-backend flow and response contract stable.
