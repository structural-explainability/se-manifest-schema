"""Validate role-capability-map.toml."""

from pathlib import Path

from se_manifest_schema.validation.validate_role_capability_map import (
    validate_role_capability_map_file,
)

__all__ = ["run"]


def run(path: Path) -> int:
    """Validate role-capability-map.toml internal consistency."""
    errors = validate_role_capability_map_file(path)

    if errors:
        print("[validate-role-capability-map] FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("[validate-role-capability-map] PASSED")
    return 0
