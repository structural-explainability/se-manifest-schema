# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

### Added - 2026-05-16

- Added repository classes for:
  - `contract`
  - `record_system`
  - `verification`
- Added support for Accountable Record application-layer repositories:
  - `se-accountable-record`
  - `judicial-record`
  - `civic-institutional-record`
  - `se-verification-judicial-record`
  - `se-verification-civic-institutional-record`
- Added manifest class rules for language-neutral contracts, domain record
  systems, and verification repositories.
- Added validation field support for:
  - `entrypoint`
  - `export_check_entrypoint`
  - `reference_entrypoint`
  - `strict_entrypoint`
  - `tag_entrypoint`

---

## [0.3.0] - 2026-05-06

### Added

- Packaged `manifest-schema.toml` into the source distribution and wheel for runtime access.
- Added command modules for `validate`, `validate-schema`, and `sync-version`.
- Added CLI command tests.

### Changed

- Refactored CLI handling into dedicated command modules.
- Replaced `.markdownlint.yml` with `.markdownlint-cli2.yaml`.
- Updated schema/package metadata for the 0.3.0 release.

### Removed

- Removed orchestration in favor of command-specific modules.

---

## [0.2.3] - 2026-05-01

### Added

Added two more `allowed_fields`:

```toml
[section.validation]
required = false
description = "Repository-local validation configuration."
allowed_fields = [
    "entrypoint",
    "strict_entrypoint",
    "tag_entrypoint",
]
```

---

## [0.2.2] - 2026-05-01

### Added

```toml
[field.validation.strict_entrypoint]
type = "string"
required = false

[field.validation.tag_entrypoint]
type = "string"
required = false
```

---

## [0.2.1] - 2026-04-30

### Added

In pyproject.toml, added:
force-include = {"manifest-schema.toml" = "se_manifest_schema/manifest-schema.toml"}

---

## [0.2.0] - 2026-04-30

### Added

- Standalone repository `se-manifest-schema` extracted from `se-constitution`
- Canonical manifest schema file: `manifest-schema.toml`
- `manifest_schema` field in `[exports]` for schema discovery
- New repository class: `manifest_schema`
- Local validation command for validating this repo `SE_MANIFEST.toml`
- Manifest loading utilities for schema and manifest validation
- `--strict` flag on `validate` command treats warnings as errors
- `--strict` enforced in pre-commit hook and CI

---

## Notes on Versioning and Releases

- We use **SemVer**:
  - **MAJOR** - breaking changes to artifact structure or validation semantics
  - **MINOR** - backward-compatible additions to schema or validation rules
  - **PATCH** - fixes, documentation, tooling
- Versions are driven by git tags. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

## Release Procedure (Required)

Follow these steps exactly when creating a new release.

### Task 1. Update release metadata (manual edits)

1.1. `manifest-schema.toml` - update `version` when schema semantics or validator contract changes
1.2. `CITATION.cff` - update `version` and `date-released`
1.3. CHANGELOG.md: add section, move unreleased entries, update links

### Task 2. Sync and Validate

Sync command reads `CITATION.cff` version and `date-released`
and updates `pyproject.toml` fallback-version.

```shell
uv sync --extra dev --extra docs --upgrade
uv run se-manifest sync-version
uv run se-manifest validate-schema --strict
uv run se-manifest validate --strict
git add -A
uvx pre-commit run --all-files
uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build

uv run python -c "import shutil; from pathlib import Path; shutil.rmtree(Path('dist'), ignore_errors=True)"

uv run python -m build
uv run python -m twine check dist/*

uv run python -c "import pathlib, zipfile; wheels=list(pathlib.Path('dist').glob('*.whl')); assert wheels, 'No wheel found'; wheel=wheels[-1]; names=zipfile.ZipFile(wheel).namelist(); print([n for n in names if n.endswith('manifest-schema.toml')]); assert 'se_manifest_schema/manifest-schema.toml' in names"
```

### Task 4. Commit, tag, push

```shell
git add -A
git commit -m "Prep X.Y.Z"
git push -u origin main
```

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

### Task 5. Verify tag consistency

```shell
uv run python -m se_manifest_schema validate --strict --require-tag
```

Confirms CITATION.cff version matches the pushed git tag.
Run this after `git push origin vX.Y.Z`; it will fail before that point.

## Only As Needed (delete a tag)

```shell
git tag -d vX.Z.Y
git push origin :refs/tags/vX.Z.Y
```

## Links

[Unreleased]: https://github.com/structural-explainability/se-manifest-schema/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.3.0
[0.2.3]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.2.3
[0.2.2]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.2.2
[0.2.1]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.2.1
[0.2.0]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.2.0
