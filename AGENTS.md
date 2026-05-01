# ./AGENTS.md

## Scope

- This repository defines constitutional rules, schemas, and validation logic.
- Changes must preserve:
  - determinism
  - cross-platform compatibility
  - data-driven definitions
- Do not introduce hidden logic where declarative structure is possible.
- Prefer explicit, inspectable structure over implicit behavior.

## WHY

- This repo uses a uniform, reproducible workflow based on **uv** and **pyproject.toml**.
- These instructions exist to prevent tool drift (e.g., pip) and OS mismatch.

## Requirements

- Use **uv** for all environment, dependency, and run commands in this repo.
- Do **not** recommend or use `pip install ...` as the primary workflow.
- The canonical Python version is defined in `.python-version`.
- Commands and guidance must work on Windows, macOS, and Linux.
- If shell-specific commands are unavoidable, provide both:
  - PowerShell (Windows)
  - bash/zsh (macOS/Linux)

## Quickstart

- Install **uv** using the official method for your OS.
- Keep uv current.
- Pin Python version for this project using uv.
- Sync dependencies (dev + docs) and upgrade.

```shell
uv self update
uv python pin $(cat .python-version)
uv sync --extra dev --extra docs --upgrade
```

## Common Tasks

Run all commands via **uv**.

Lint / format:

```shell
uv run python -m ruff format .
uv run python -m ruff check . --fix
```

Build documentation:

```shell
uv run python -m zensical build
```

## pre-commit

- pre-commit runs only on tracked / staged files.
- Developers should `git add -A` files before expecting hooks to run.
