"""sync.py - Version sync.

Source of truth: CITATION.cff version field (updated manually before release).
Targets: pyproject.toml fallback-version.

Does NOT touch:
  - CITATION.cff (that is the source, not a target)
  - schema/manifest-1.toml
  - SE_MANIFEST.toml
"""

from pathlib import Path
import re
from typing import Any, cast


def get_version_from_citation() -> str:
    """Read canonical version from CITATION.cff.

    CITATION.cff is the version source of truth for this repo.
    Update it manually as Task 1 of the release procedure.
    """
    import yaml  # requires PyYAML (dev dependency)

    path = Path("CITATION.cff")
    if not path.exists():
        raise FileNotFoundError("CITATION.cff not found")

    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("CITATION.cff must be a YAML mapping")

    typed = cast(dict[str, object], raw)
    version = typed.get("version")
    if not isinstance(version, str):
        raise ValueError("CITATION.cff missing or invalid 'version'")

    return version


def sync_pyproject(version: str) -> None:
    """Update fallback-version in pyproject.toml."""
    path = Path("pyproject.toml")
    if not path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'(fallback-version\s*=\s*")[^"]*(")',
        rf"\g<1>{version}\g<2>",
        text,
    )
    if count == 0:
        raise ValueError("pyproject.toml: could not find fallback-version field")
    if count > 1:
        raise ValueError(
            f"pyproject.toml: found {count} fallback-version fields; expected exactly 1"
        )
    path.write_text(updated, encoding="utf-8")


def sync_all() -> None:
    """Sync pyproject.toml from CITATION.cff version.

    CITATION.cff is updated manually.
    This propagates that version to pyproject.toml fallback-version.
    Nothing else is touched.
    """
    version = get_version_from_citation()
    sync_pyproject(version)
    print(f"[sync] pyproject.toml fallback-version updated to {version}")  # noqa: T201
