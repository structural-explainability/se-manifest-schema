"""commands/validate_schema.py - Validate manifest-schema.toml."""

from pathlib import Path
from typing import cast

from se_manifest_schema.load import load_toml, repo_root_schema_path
from se_manifest_schema.types.manifest_schema import ManifestSchemaData
from se_manifest_schema.validate_schema import validate_schema_internal

__all__ = ["run"]


def run(*, strict: bool = False) -> int:
    """Validate manifest-schema.toml internal consistency."""
    _ = strict

    schema_path = repo_root_schema_path()
    if schema_path is None:
        print(  # noqa: T201
            "[validate-schema] ERROR: manifest-schema.toml source file not found."
        )
        return 1

    schema = cast(ManifestSchemaData, load_toml(Path(schema_path)))
    errors = validate_schema_internal(schema)

    if errors:
        print("[validate-schema] FAILED")  # noqa: T201
        for error in errors:
            print(f"- {error}")  # noqa: T201
        return 1

    print("[validate-schema] OK")  # noqa: T201
    return 0
