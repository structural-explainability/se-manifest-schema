"""types/manifest_schema.py - Manifest schema artifact structure.

Represents the manifest schema artifact as loaded from TOML.
Uses functional TypedDict syntax because "class" is a real TOML key.
Kept in its own file because manifest schema is a distinct constitutional
artifact with a stable repeated entry shape.
"""

from typing import TypedDict

from se_manifest_schema.types.primitives import ArtifactMeta


class ManifestSectionEntry(TypedDict, total=False):
    """Manifest section definition."""

    required: bool
    description: str
    allowed_fields: list[str]


class ManifestFieldEntry(TypedDict, total=False):
    """Manifest field definition."""

    type: str
    required: bool
    constraints: list[str]


class ManifestClassEntry(TypedDict, total=False):
    """Class-specific manifest requirements."""

    required_repo_name_patterns: list[str]
    required_layer_roles: list[str]
    required_sections: list[str]
    optional_sections: list[str]
    forbidden_sections: list[str]
    required_compatibility_fields: list[str]


ManifestSchemaData = TypedDict(
    "ManifestSchemaData",
    {
        "meta": ArtifactMeta,
        "manifest": dict[str, object],
        "section": dict[str, ManifestSectionEntry],
        "field": dict[str, ManifestFieldEntry],
        "class": dict[str, ManifestClassEntry],
    },
    total=False,
)
