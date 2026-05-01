"""load.py - Loading and parsing for se-manifest-schema.

Owns:
  - load_toml()        - read any TOML file
  - load_schema()      - read manifest-schema.toml
  - load_manifest()    - read SE_MANIFEST.toml
  - get_repo_version() - extract repo.version
  - get_git_tag()      - read current exact git tag
"""

from pathlib import Path
import shutil
import subprocess
import tomllib
from typing import Any, cast


def load_toml(path: Path) -> dict[str, Any]:
    """Load and return TOML data from the specified path."""
    return tomllib.loads(path.read_text(encoding="utf-8"))


def load_schema() -> dict[str, Any]:
    """Load manifest-schema.toml from repo root."""
    path = Path("manifest-schema.toml")
    if not path.exists():
        raise FileNotFoundError("manifest-schema.toml not found")
    return load_toml(path)


def load_manifest() -> dict[str, Any]:
    """Load SE_MANIFEST.toml from repo root."""
    path = Path("SE_MANIFEST.toml")
    if not path.exists():
        raise FileNotFoundError("SE_MANIFEST.toml not found")
    return load_toml(path)


def get_repo_version(manifest: dict[str, Any]) -> str:
    """Extract and validate repo.version from manifest."""
    repo = manifest.get("repo")
    if not isinstance(repo, dict):
        raise ValueError("SE_MANIFEST.toml missing or invalid [repo] section")
    typed: dict[str, object] = cast(dict[str, object], repo)
    version = typed.get("version")
    if not isinstance(version, str):
        raise ValueError("SE_MANIFEST.toml missing or invalid repo.version")
    return version


def get_git_tag() -> str:
    """Return the current git tag (exact match required)."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git executable not found on PATH")
    try:
        return (
            subprocess.check_output(  # noqa: S603
                [git, "describe", "--tags", "--exact-match"],
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Repository is not on a tagged commit") from exc
