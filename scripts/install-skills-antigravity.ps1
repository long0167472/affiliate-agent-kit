param(
    [ValidateSet('Workspace', 'Global', 'Both')]
    [string]$Target = 'Both',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $repoRoot 'skills'
$skillDirs = Get-ChildItem -LiteralPath $sourceRoot -Directory | Where-Object { $_.Name -like 'aff-*' }

$destinations = @()
if ($Target -in @('Workspace', 'Both')) {
    $destinations += (Join-Path $repoRoot '.agents\skills')
}
if ($Target -in @('Global', 'Both')) {
    $destinations += (Join-Path $HOME '.gemini\config\skills')
}

# Skill descriptions optimized for Antigravity progressive disclosure trigger
$triggers = @{
    'aff-orchestrator' = 'Coordinate specialist affiliate agents from product selection to creative tests, spawn independent cross-reviewers at handoffs, and maintain a measurable learning loop for TikTok Shop and Shopee Video affiliate workflows. Use this skill when orchestrating or managing the end-to-end affiliate video lifecycle, cycles, and daily reviews.'
    'aff-product-intelligence' = 'Independently discover, screen and select affiliate products for TikTok Shop and Shopee Video, grounding every creative claim in current product evidence and expected unit economics. Use this skill when researching, screening, or selecting products/SKUs for affiliate marketing.'
    'aff-creative-strategist' = 'Develop evidence-backed short-video concepts, hooks, frame-level storyboards and testable creative hypotheses for an affiliate product. Use this skill when designing concepts, hooks, and storyboards for TikTok Shop or Shopee Video.'
    'aff-video-producer' = 'Turn an affiliate storyboard and permitted footage into platform-native short videos with shot-level quality control and traceable source assets. Use this skill when producing, editing, rendering, or checking affiliate video assets with Remotion/FFmpeg.'
    'aff-publisher' = 'Prepare and publish approved affiliate videos to TikTok Shop or Shopee Video using verified account capabilities, correct product attachment and platform disclosures. Use this skill when preparing, validating, or executing publishing workflows for affiliate posts with attached products.'
    'aff-growth-analyst' = 'Measure affiliate video performance, evaluate hook and creative experiments, and propose the next test without mistaking platform variability for causal lift. Use this skill when analyzing video metrics, commission settlement, daily cohort reviews, and A/B test results.'
    'aff-creative-reviewer' = 'Independently cross-review affiliate product briefs, storyboards, rendered videos and experiment conclusions for evidence, viewer appeal and testability. Use this skill when independently reviewing, QA-ing, or challenging artifacts at handoff boundaries.'
}

foreach ($dest in $destinations) {
    if (-not (Test-Path -LiteralPath $dest)) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
    }

    foreach ($dir in $skillDirs) {
        $skillName = $dir.Name
        $targetSkillDir = Join-Path $dest $skillName
        
        if ((Test-Path -LiteralPath $targetSkillDir) -and -not $Force) {
            Write-Output "Skill already exists at $targetSkillDir. Skipping (use -Force to overwrite)."
            continue
        }

        if (-not (Test-Path -LiteralPath $targetSkillDir)) {
            New-Item -ItemType Directory -Path $targetSkillDir -Force | Out-Null
        }

        # Read original SKILL.md
        $sourceSkillMd = Join-Path $dir.FullName 'SKILL.md'
        $content = Get-Content -LiteralPath $sourceSkillMd -Raw -Encoding UTF8

        # If trigger description exists in map, update description
        if ($triggers.ContainsKey($skillName)) {
            $newDesc = $triggers[$skillName]
            $content = $content -replace '(?ms)^description:.*?(?=\r?\n---)', "description: $newDesc"
        }

        $targetSkillMd = Join-Path $targetSkillDir 'SKILL.md'
        [System.IO.File]::WriteAllText($targetSkillMd, $content, [System.Text.Encoding]::UTF8)

        # Copy references
        $sourceRefs = Join-Path $dir.FullName 'references'
        $targetRefs = Join-Path $targetSkillDir 'references'
        if (Test-Path -LiteralPath $sourceRefs) {
            if (-not (Test-Path -LiteralPath $targetRefs)) {
                New-Item -ItemType Directory -Path $targetRefs -Force | Out-Null
            }
            Get-ChildItem -LiteralPath $sourceRefs -File | ForEach-Object {
                Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $targetRefs $_.Name) -Force
            }
        }

        Write-Output "Installed $skillName -> $targetSkillDir"
    }
}
Write-Output "Antigravity skills installation completed successfully."
