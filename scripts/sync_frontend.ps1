param(
    [Parameter(Mandatory = $true)]
    [string]$BucketName
)

$syncArgs = @(
    "s3",
    "sync",
    "frontend/",
    "s3://$BucketName",
    "--delete",
    "--exclude",
    "config.example.js",
    "--exclude",
    ".env",
    "--exclude",
    ".env.*",
    "--exclude",
    "*.map",
    "--exclude",
    ".DS_Store",
    "--exclude",
    "Thumbs.db"
)

Write-Output "Syncing frontend/ to s3://$BucketName"
aws @syncArgs
