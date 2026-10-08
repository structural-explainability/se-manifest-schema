#Requires -Version 7.0

<#
rel.ps1 - Local release validation for se-manifest-schema.
Run .\sit.ps1 separately first. This script does not publish or create tags.
It checks release metadata, package contents, and wheel installation.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-ReleaseStep {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [scriptblock]$Action
    )

    Write-Host "`n============================================================"
    Write-Host $Name
    Write-Host '============================================================'
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed (exit code $LASTEXITCODE)."
    }
}

function Assert-NativeSuccess {
    param([Parameter(Mandatory)] [string]$Description)
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed (exit code $LASTEXITCODE)."
    }
}

# A) Release-specific repository checks (not repeated from sit.ps1).
Invoke-ReleaseStep 'A1) Update and pin GitHub Actions' {
    uvx gha-tools autoupdate --pin=all --write .github/workflows
}
# A2) Audit GitHub Actions
uvx zizmor@latest .github/

if ($LASTEXITCODE -notin @(0, 11)) {
    throw "A2) Audit GitHub Actions failed (exit code $LASTEXITCODE)."
}
Invoke-ReleaseStep 'A3) Verify committed lockfile' {
    uv sync --locked
}
Invoke-ReleaseStep 'A4) Validate role-capability map' {
    uv run --locked se-manifest validate-role-capability-map
}
Invoke-ReleaseStep 'A5) Validate manifest schema' {
    uv run --locked se-manifest validate-schema --strict
}
Invoke-ReleaseStep 'A6) Validate repository manifest' {
    uv run --locked se-manifest validate-manifest --strict
}
Invoke-ReleaseStep 'A7) Check canonical version metadata' {
    uv run --locked se-manifest check-version
}
# verify-graph is intentionally not a release gate.
Invoke-ReleaseStep 'A8) Generate CODEOWNERS' {
    uvx se-codeowners generate --strict --output .github/CODEOWNERS
}
Invoke-ReleaseStep 'A9) Check CODEOWNERS' {
    uvx se-codeowners check
}

# B) Additional local reports retained from the previous rel.ps1.
# B1) Check for dead code (advisory)
uvx vulture src/se_manifest_schema --min-confidence 60

if ($LASTEXITCODE -notin @(0, 3)) {
    throw "B1) Check for dead code failed (exit code $LASTEXITCODE)."
}
Invoke-ReleaseStep 'B2) Report C-or-worse complexity' {
    uvx radon cc src/se_manifest_schema -s -a -n C
}
Invoke-ReleaseStep 'B3) Report raw code metrics' {
    # uvx radon raw src/se_manifest_schema
}

# C) Build clean distributions. Do not stage, commit, or tag changes.
Write-Host "`n============================================================"
Write-Host 'C1) Remove old distributions'
Write-Host '============================================================'
Remove-Item -LiteralPath 'dist' -Recurse -Force -ErrorAction SilentlyContinue

Invoke-ReleaseStep 'C2) Build wheel and source distribution' {
    uv build
}

# D) Inspect the same artifact locations checked in Linux pre-release CI.
$artifactCheck = @'
from pathlib import Path
from tarfile import open as open_tar
from zipfile import ZipFile
wheels = list(Path("dist").glob("*.whl"))
sdists = list(Path("dist").glob("*.tar.gz"))
assert len(wheels) == 1, f"Expected one wheel, found {len(wheels)}"
assert len(sdists) == 1, f"Expected one sdist, found {len(sdists)}"
wheel_version = wheels[0].name.split("-")[1]
sdist_version = sdists[0].name.removesuffix(".tar.gz").rsplit("-", 1)[1]
assert wheel_version == sdist_version, "Wheel and sdist versions differ"

with ZipFile(wheels[0]) as archive:
    expected = "se_manifest_schema/manifest-schema.toml"
    assert expected in archive.namelist(), f"Wheel missing {expected}"

with open_tar(sdists[0], "r:gz") as archive:
    matches = [
        name for name in archive.getnames()
        if name.count("/") == 1 and name.endswith("/manifest-schema.toml")
    ]
    assert len(matches) == 1, f"Expected root-level schema in sdist; found {matches}"

print(f"Wheel: {wheels[0].name}")
print(f"Sdist: {sdists[0].name}")
print(f"Matching artifact version: {wheel_version}")
print("Artifact versions and schema locations verified.")
'@

Write-Host "`n============================================================"
Write-Host 'D1) Check artifact versions and schema contents'
Write-Host '============================================================'
$artifactCheck | uv run --locked python -
Assert-NativeSuccess 'Artifact inspection'

Invoke-ReleaseStep 'D2) Check distribution metadata with Twine' {
    $artifacts = @(Get-ChildItem -LiteralPath 'dist' -File |
        Where-Object { $_.Name -match '\.(whl|tar\.gz)$' } |
        Select-Object -ExpandProperty FullName)
    if ($artifacts.Count -ne 2) {
        throw "Expected two distributions; found $($artifacts.Count)."
    }
    uvx twine check @artifacts
}

# E) Verify schema accessibility from the installed wheel, not the src checkout.
Write-Host "`n============================================================"
Write-Host 'E1) Install wheel in isolated environment and load schema'
Write-Host '============================================================'
$testEnv = Join-Path ([System.IO.Path]::GetTempPath()) ("se-manifest-wheel-" + [guid]::NewGuid().ToString('N'))
try {
    $interpreter = (uv python find | Select-Object -First 1).Trim()
    Assert-NativeSuccess 'Find Python interpreter'
    uv venv --python $interpreter $testEnv
    Assert-NativeSuccess 'Create isolated environment'

    $testPython = Join-Path $testEnv 'Scripts/python.exe'
    $wheel = (Get-ChildItem -LiteralPath 'dist' -Filter '*.whl' -File | Select-Object -First 1).FullName
    uv pip install --python $testPython --no-deps $wheel
    Assert-NativeSuccess 'Install built wheel'

    $installedCheck = @'
import tomllib
from importlib.resources import files

schema = files("se_manifest_schema").joinpath("manifest-schema.toml")
document = tomllib.loads(schema.read_text(encoding="utf-8"))
assert document, "Installed schema is empty"
print("Installed wheel schema loaded and parsed successfully.")
'@
    $installedCheck | & $testPython -
    Assert-NativeSuccess 'Installed wheel schema test'
}
finally {
    Remove-Item -LiteralPath $testEnv -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "`nRelease validation completed successfully. No release was published."
