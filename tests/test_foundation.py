from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_foundation_files_exist() -> None:
    expected_paths = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "pyproject.toml",
        REPO_ROOT / "template.yaml",
        REPO_ROOT / "backend" / "__init__.py",
        REPO_ROOT / "docs" / "architecture.md",
        REPO_ROOT / "docs" / "implementation-plan.md",
    ]

    missing = [path for path in expected_paths if not path.exists()]

    assert not missing, f"Missing expected foundation files: {missing}"
