param(
    [string]$Destination = (Join-Path $HOME '.codex\skills'),
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $repoRoot 'skills'
$skillDirs = Get-ChildItem -LiteralPath $sourceRoot -Directory | Where-Object { $_.Name -like 'aff-*' }

if (-not (Test-Path -LiteralPath $Destination)) {
    New-Item -ItemType Directory -Path $Destination | Out-Null
}

foreach ($dir in $skillDirs) {
    $target = Join-Path $Destination $dir.Name
    if ((Test-Path -LiteralPath $target) -and -not $Force) {
        throw "Skill already exists: $target. Re-run with -Force to update it."
    }
    if (Test-Path -LiteralPath $target) {
        Copy-Item -LiteralPath (Join-Path $dir.FullName 'SKILL.md') -Destination (Join-Path $target 'SKILL.md') -Force
        $refsTarget = Join-Path $target 'references'
        if (-not (Test-Path -LiteralPath $refsTarget)) {
            New-Item -ItemType Directory -Path $refsTarget | Out-Null
        }
        Get-ChildItem -LiteralPath (Join-Path $dir.FullName 'references') -File | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $refsTarget $_.Name) -Force
        }
    } else {
        Copy-Item -LiteralPath $dir.FullName -Destination $target -Recurse
    }
    Write-Output "Installed $($dir.Name)"
}
