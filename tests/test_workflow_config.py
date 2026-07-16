from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_ci_workflow_contains_pull_request_validation_and_no_oidc() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "pull_request:" in workflow
    assert "- main" in workflow
    assert "id-token: write" not in workflow
    assert "actions/setup-python@v6" in workflow
    assert "uv sync --frozen" in workflow
    assert "uv run ruff check ." in workflow
    assert "uv run ruff format --check ." in workflow
    assert "uv run mypy ." in workflow
    assert "uv run pytest" in workflow
    assert "sam validate" in workflow
    assert "sam build" in workflow


def test_production_deploy_workflow_uses_separate_roles_and_orders_backend_first() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")

    assert "push:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "id-token: write" in workflow
    assert "group: production-deployment" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "aws-actions/configure-aws-credentials@v6.2.1" in workflow
    assert "AWS_BACKEND_DEPLOY_ROLE_ARN" in workflow
    assert "AWS_CLOUDFORMATION_EXECUTION_ROLE_ARN" in workflow
    assert "AWS_FRONTEND_DEPLOY_ROLE_ARN" in workflow
    assert "SAM_STACK_NAME" in workflow
    assert "SAM_ARTIFACT_BUCKET" in workflow
    assert "sam deploy \\" in workflow
    assert '--stack-name "$SAM_STACK_NAME"' in workflow
    assert "--no-resolve-s3" in workflow
    assert '--s3-bucket "$SAM_ARTIFACT_BUCKET"' in workflow
    assert '--role-arn "$AWS_CLOUDFORMATION_EXECUTION_ROLE_ARN"' in workflow
    assert "python scripts/check_backend_endpoint.py" in workflow
    assert 'aws s3 sync frontend/ "s3://$AWS_FRONTEND_BUCKET" --delete' in workflow
    assert '--exclude "config.example.js"' in workflow
    assert "python scripts/check_frontend_website.py" in workflow
    assert "Configure AWS credentials for backend deployment" in workflow
    assert "Configure AWS credentials for frontend sync" in workflow


def test_bootstrap_template_restricts_trust_and_defines_separate_deploy_roles() -> None:
    template = (REPO_ROOT / "bootstrap" / "github-frontend-deploy-iam.yaml").read_text(
        encoding="utf-8"
    )
    subject_restriction = (
        "token.actions.githubusercontent.com:sub: !Sub "
        "repo:${GitHubRepositoryOwner}/${GitHubRepositoryName}:ref:refs/heads/main"
    )

    assert "token.actions.githubusercontent.com:aud: sts.amazonaws.com" in template
    assert subject_restriction in template
    assert "RoleName: aws-cloud-ai-web-github-frontend-deploy" in template
    assert "RoleName: aws-cloud-ai-web-github-backend-deploy" in template
    assert "RoleName: aws-cloud-ai-web-cloudformation-execution" in template
    assert "Service: cloudformation.amazonaws.com" in template
    assert "iam:PassRole" in template
    assert "cloudformation:CreateChangeSet" in template
    assert "- s3:ListBucket" in template
    assert "- s3:GetBucketLocation" in template
    assert "- s3:PutObject" in template
    assert "- s3:DeleteObject" in template
