"""validate_contract.py - Version and tag alignment for se-manifest-schema.

Checks that CITATION.cff version matches the current git tag.
Called by orchestrate.py when --require-tag is passed.
"""

from typing import Any

from se_manifest_schema.load import get_git_tag
from se_manifest_schema.sync import get_version_from_citation


def validate_tag(manifest: dict[str, Any]) -> list[str]:
    """Validate CITATION.cff version matches current git tag."""
    _ = manifest  # not needed; version comes from CITATION.cff
    errors: list[str] = []
    try:
        version = get_version_from_citation()
    except (FileNotFoundError, ValueError) as e:
        errors.append(str(e))
        return errors
    try:
        tag = get_git_tag()
        if tag != f"v{version}":
            errors.append(
                f"CITATION.cff version ({version}) does not match git tag ({tag})"
            )
    except RuntimeError as e:
        errors.append(str(e))
    return errors
