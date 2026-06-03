#Requires -Version 7.0

<#
Run the release validation sequence.

The script echoes each exact command before running it.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Section,

        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Script
    )

    Write-Host ""
    Write-Host "============================================================"
    Write-Host $Section
    Write-Host "============================================================"
    Write-Host $Command
    & $Script
}

# ============================================================
# A) Toolchain refresh
# ============================================================

Invoke-Step "A1) Sync Python tooling" "uv sync --extra dev --extra docs --upgrade" {
    uv sync --extra dev --extra docs --upgrade
}

Invoke-Step "A2) Install pre-commit hooks" "uvx pre-commit install" {
    uvx pre-commit install
}

# ============================================================
# C) Package command surface and manifest validation
# ============================================================

Invoke-Step "C1) Validate role capability map" "uv run se-manifest validate-role-capability-map" {
    uv run se-manifest validate-role-capability-map
}

Invoke-Step "C2) Verify manifest dependency graph" "uv run se-manifest verify-graph" {
    uv run se-manifest verify-graph
}

Invoke-Step "C3) Validate manifest schema" "uv run se-manifest validate-schema --strict" {
    uv run se-manifest validate-schema --strict
}

Invoke-Step "C4) Validate SE manifests" "uv run se-manifest validate-manifest --strict" {
    uv run se-manifest validate-manifest --strict
}

Invoke-Step "C5) Check version metadata" "uv run se-manifest check-version" {
    uv run se-manifest check-version
}

# ============================================================
# D) Pre-commit and Python tests
# ============================================================

Invoke-Step "D1) Stage all changes so pre-commit sees tracked/staged files" "git add -A" {
    git add -A
}

Invoke-Step "D2) Run pre-commit checks" "uvx pre-commit run --all-files" {
    uvx pre-commit run --all-files
}

Invoke-Step "D3) Run pre-commit checks again after autofixes" "uvx pre-commit run --all-files" {
    uvx pre-commit run --all-files
}

Invoke-Step "D4) Run Python tests" "uv run python -m pytest" {
    uv run python -m pytest
}

Invoke-Step "D5) Run Pyright" "uv run python -m pyright" {
    uv run python -m pyright
}

Invoke-Step "D6) Run final pre-commit check after tests/type checks" "uvx pre-commit run --all-files" {
    uvx pre-commit run --all-files
}

# ============================================================
# E) Documentation
# ============================================================

Invoke-Step "E1) Build documentation" "uv run python -m zensical build" {
    uv run python -m zensical build
}

# ============================================================
# F) Architectural and code-health checks
# ============================================================

# Invoke-Step "F0) check import layers" "uvx --python 3.13 --from import-linter lint-imports --config .github/.importlinter" {
#     uvx --python 3.13 --from import-linter lint-imports --config .github/.importlinter
# }
Invoke-Step "F1) Find dead code" "uvx --with-editable . vulture src/se_manifest_schema" {
    uvx --with-editable . vulture src/se_manifest_schema
}

Invoke-Step "F2) Check complexity; any output means C-or-worse complexity exists" "uvx radon cc src/se_manifest_schema -s -a -n C" {
    uvx radon cc src/se_manifest_schema -s -a -n C
}

Invoke-Step "F3) Report raw code metrics" "uvx radon raw src/se_manifest_schema -j | uv run python -c `"import json, sys; data=json.load(sys.stdin); keys=('loc','lloc','sloc','comments','multi','blank','single_comments'); totals={k:sum(file[k] for file in data.values()) for k in keys}; print('\n'.join(f'{k.upper()}: {v}' for k,v in totals.items()))`"" {
    uvx radon raw src/se_manifest_schema -j | uv run python -c "import json, sys; data=json.load(sys.stdin); keys=('loc','lloc','sloc','comments','multi','blank','single_comments'); totals={k:sum(file[k] for file in data.values()) for k in keys}; print('\n'.join(f'{k.upper()}: {v}' for k,v in totals.items()))"
}

# ============================================================
# G) Distribution artifacts
# ============================================================

Invoke-Step "G1) Build source and wheel distributions" "uv build" {
    uv build
}

Invoke-Step "G2) Check distribution metadata" "uvx twine check dist/*" {
    uvx twine check dist/*
}

Write-Host ""
Write-Host "============================================================"
Write-Host "Release validation completed successfully."
Write-Host "============================================================"
