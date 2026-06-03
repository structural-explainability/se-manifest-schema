# se-manifest-schema

[![PyPI](https://img.shields.io/pypi/v/se-manifest-schema?logo=pypi&label=pypi)](https://pypi.org/project/se-manifest-schema/)
[![Docs Site](https://img.shields.io/badge/docs-site-blue?logo=github)](https://structural-explainability.github.io/se-manifest-schema/)
[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/structural-explainability/se-manifest-schema)
[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](./pyproject.toml)
[![Python 3.14 Ready](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/python-315-ready.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/python-315-ready.yml)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

[![CI](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/ci-python-zensical.yml)
[![Docs-Deploy](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/deploy-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/deploy-zensical.yml)
[![Pre-Release](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/pre-release.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/pre-release.yml)
[![Release](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/release-pypi.yml/badge.svg)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/release-pypi.yml)
[![Links](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/links.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/links.yml)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-brightgreen.svg)](https://github.com/structural-explainability/se-manifest-schema/security)

> Structural Explainability (SE) Manifest Schema

This repository defines the canonical `SE_MANIFEST.toml` schema
for the Structural Explainability ecosystem.

It is the first dependency layer in the SE repository graph.
It has no upstream SE dependencies and exists
so foundational repositories can validate their
manifests without depending on `se-constitution`.

The schema is maintained in:

- [`manifest-schema.toml`](./manifest-schema.toml)

## Validate SE_MANIFEST.toml in a Repository

```shell
uvx se-manifest-schema validate-manifest --path SE_MANIFEST.toml --strict
```

## Developer Command Reference

<details>
<summary>Show command reference</summary>

### In a machine terminal

Open a machine terminal where you want the project:

```shell
git clone https://github.com/structural-explainability/se-manifest-schema

cd se-manifest-schema
code .
```

### In a VS Code terminal

```shell
uv self update
uv python pin 3.14
uv sync --extra dev --extra docs --upgrade

uvx pre-commit install

git add -A
uvx pre-commit run --all-files
# repeat if changes were made
uvx pre-commit run --all-files

# validate the role capability map
uv run se-manifest validate-role-capability-map

# verify the manifest dependency graph
uv run se-manifest verify-graph

# validate schema
uv run se-manifest validate-schema --strict

# validate manifest (all repos)
uv run se-manifest validate-manifest --strict

# types, tests, docs
uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build

# save progress
git add -A
git commit -m "update"
git push -u origin main
```

Merging GH Agent code example

```shell
git fetch origin copilot/analyze-test-coverage
git switch copilot/analyze-test-coverage
uv sync --extra dev --extra docs --upgrade
uvx pre-commit run --all-files
git status

git add -A
uvx pre-commit run --all-files
uv run python -m pyright
uv run python -m pytest
uv run se-manifest validate-schema --strict
uv run se-manifest validate-manifest --strict
uv run python -m zensical build

git add -A
git commit -m "fix copilot generated test formatting"
git push
```

</details>

## Citation

[CITATION.cff](./CITATION.cff)

## License

[LICENSE](./LICENSE)

## Manifest

[SE_MANIFEST.toml](./SE_MANIFEST.toml)
