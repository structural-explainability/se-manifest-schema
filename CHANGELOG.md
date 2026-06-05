# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

---

## [0.5.0] - 2026-06-02

This release tightens the public `SE_MANIFEST.toml` contract
and removes shorthand from the manifest schema.
Adds schema_version.

## Changed

- Renamed the repository identity section from `[repo]` to `[repository]`.
- Replaced abbreviated repository class value `spec` with `specification`.
- Updated schema field definitions and class requirements to use `repository`.
- Added the preferred package-matching CLI command:

  ```shell
  uvx se-manifest-schema validate-manifest --path SE_MANIFEST.toml --strict
  ```

- Kept `se-manifest` as a compatibility command alias.
- Made structured dependency records the only valid dependency declaration form.

## Added

- Added optional `[governance].authority_manifest` for repositories that
  declare an authority-surface manifest such as `.accountability/surfaces.toml`.

## Removed

- Removed acceptance of legacy string dependencies in `[depends].required`
  and `[depends].optional`.
- Removed migration language for legacy dependency strings
  from `manifest-schema.toml`.

## Migration

Update manifests from:

```toml
[repo]
class = "spec"
```

to:

```toml
[repository]
class = "specification"
```

Update dependencies from:

```toml
[depends]
required = [
  "structural-explainability/example@main",
]
optional = []
```

to:

```toml
[depends]
required = [
  { repository = "structural-explainability/example", kind = "semantic", version = "main", reason = "Declares the upstream semantic dependency." },
]
optional = []
```

If the repository declares an authority-surface manifest, add:

```toml
[governance]
authority_manifest = ".accountability/surfaces.toml"
```

and include the file in `[provides].artifacts`.

---

## [0.4.2] - 2026-05-30

### Added

- added class.paper

---

## [0.4.1] - 2026-05-23

### Added

- added to class.admin the .github repo

---

## [0.4.0] - 2026-05-23

### Added

- Added repository class support for generic contract engine repositories:
  - `engine`
- Added manifest class rules for contract engine repositories, including:
  - `se-{focus}-kit`
  - `se-{focus}-engine`
- Added contract role support for:
  - `authority`
  - `domain-contract`
- Added contract validation rules requiring contract repositories to declare:
  - `contract_role`
  - `contract_authority`
  - `contract_version`
- Added contract validation rules distinguishing root contract authorities from
  domain contracts:
  - contract authorities must not consume another contract
  - domain contracts must consume one upstream contract
  - domain contracts must not consume themselves
  - contract authority must equal the repository's own name

### Changed

- Updated contract repository name patterns to allow `*-record`
  repositories, including `accountable-record`, `judicial-record`, and
  `civic-record`, to declare `class = "contract"` when they define contracts
  rather than operational record systems.
- Updated manifest filename validation to allow both supported manifest names:
  - `SE_MANIFEST.toml`
  - `MANIFEST.toml`
- Replaced exact manifest filename validation with allowed manifest filename
  validation.
- Clarified that repository class is declared explicitly by `repository.class`; name
  patterns validate compatibility with the declared class and are not the sole
  source of class inference.

---

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
1.4. `pyproject.toml` - update build system `fallback-version`

### Task 2. Validate

```shell
uv sync --extra dev --extra docs --upgrade
uvx pre-commit install

uv run se-manifest validate-role-capability-map
uv run se-manifest validate-schema --strict
uv run se-manifest validate-manifest --strict
uv run se-manifest check-version
# uv run se-manifest verify-graph is NOT required to pass

# generate and check CODEOWNERS
uvx se-codeowners generate --strict --output .github/CODEOWNERS
uvx se-codeowners check

git add -A
uvx pre-commit run --all-files
uvx pre-commit run --all-files

uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build

uv run python -c "import shutil; from pathlib import Path; shutil.rmtree(Path('dist'), ignore_errors=True)"

uv run python -m build
uv run python -m twine check dist/*

uv run python -c "import pathlib, zipfile; wheels=list(pathlib.Path('dist').glob('*.whl')); assert wheels, 'No wheel found'; wheel=wheels[-1]; names=zipfile.ZipFile(wheel).namelist(); print([n for n in names if n.endswith('manifest-schema.toml')]); assert 'se_manifest_schema/manifest-schema.toml' in names"
```

### Task 4. Commit, push, tag

```shell
git add -A
git commit -m "Prepare X.Y.Z"
git push -u origin main
```

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

### Task 5. Verify tag consistency

```shell
uv run se-manifest check-version --require-tag
```

Confirms CITATION.cff version matches the pushed git tag.
Run this after `git push origin vX.Y.Z`; it will fail before that point.

## Only As Needed (delete a tag)

```shell
git tag -d vX.Z.Y
git push origin :refs/tags/vX.Z.Y
```

## Links

[Unreleased]: https://github.com/structural-explainability/se-manifest-schema/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.5.0
[0.4.2]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.4.2
[0.4.1]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.4.1
[0.4.0]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.4.0
[0.3.0]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.3.0
[0.2.3]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.2.3
[0.2.2]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.2.2
[0.2.1]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.2.1
[0.2.0]: https://github.com/structural-explainability/se-manifest-schema/releases/tag/v0.2.0

<!-- markdownlint-enable MD024 -->
