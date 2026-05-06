# se-manifest-schema

[![PyPI](https://img.shields.io/pypi/v/se-manifest-schema?logo=pypi&label=pypi)](https://pypi.org/project/se-manifest-schema/)
[![Docs Site](https://img.shields.io/badge/docs-site-blue?logo=github)](https://structural-explainability.github.io/se-manifest-schema/)
[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/structural-explainability/se-manifest-schema)
[![Python 3.15+](https://img.shields.io/badge/python-3.15%2B-blue?logo=python)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

[![CI](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/ci-python-zensical.yml)
[![Docs](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/deploy-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/deploy-zensical.yml)
[![Release](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/release-pypi.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/release-pypi.yml)
[![Links](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/links.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-manifest-schema/actions/workflows/links.yml)

> Structural Explainability (SE) Manifest Schema

This repository defines the canonical `SE_MANIFEST.toml` schema
for the Structural Explainability ecosystem.

It is the first dependency layer in the SE repository graph.
It has no upstream SE dependencies and exists
so foundational repositories can validate their
manifests without depending on `se-constitution`.

The schema is maintained in:

- [`manifest-schema.toml`](./manifest-schema.toml)

## Command Reference

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
# reset uv cache only after suspected cache corruption or strange dependency errors
# uv cache clean

uv self update
uv python pin 3.15
uv sync --extra dev --extra docs --upgrade

uvx pre-commit install

git add -A
uvx pre-commit run --all-files
# repeat if changes were made
git add -A
uvx pre-commit run --all-files

# validate
uv run python -m se_manifest_schema validate --strict

# validate schema source of truth (this repo only)
uv run se-manifest validate-schema --strict

# validate repo SE_MANIFEST.toml against schema (also used downstream)
uv run se-manifest validate --strict

# do chores
uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build

# save progress
git add -A
git commit -m "update"
git push -u origin main
```

</details>

## Citation

[CITATION.cff](./CITATION.cff)

## License

[LICENSE](./LICENSE)

## Manifest

[SE_MANIFEST.toml](./SE_MANIFEST.toml)
