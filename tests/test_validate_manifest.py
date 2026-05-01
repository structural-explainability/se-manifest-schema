"""Tests for validate_manifest.py - SE_MANIFEST.toml conformance."""

from typing import Any, cast

from se_manifest_schema.load import load_manifest, load_schema
from se_manifest_schema.types.manifest_schema import ManifestSchemaData
from se_manifest_schema.validate_manifest import validate_manifest


def _minimal_schema() -> ManifestSchemaData:
    return cast(
        ManifestSchemaData,
        {
            "manifest": {
                "identity": {
                    "schema_required": True,
                    "schema_allowed": ["se-manifest-2"],
                    "schema_url_required": True,
                }
            },
            "section": {
                "repo": {"required": True, "allowed_fields": ["name", "class"]},
                "scope": {"required": True, "allowed_fields": ["includes", "excludes"]},
            },
            "field": {
                "repo": {
                    "name": {"type": "string", "required": True},
                    "class": {"type": "string", "required": True},
                },
                "scope": {
                    "includes": {"type": "list[string]", "required": True},
                    "excludes": {"type": "list[string]", "required": True},
                },
            },
            "class": {
                "test_class": {
                    "required_sections": ["repo", "scope"],
                    "optional_sections": [],
                    "forbidden_sections": [],
                }
            },
            "validation": {
                "require_known_sections_only": True,
                "require_known_fields_only": True,
            },
        },
    )


def _minimal_manifest() -> dict[str, Any]:
    return {
        "schema": "se-manifest-2",
        "schema_url": "https://example.com",
        "repo": {"name": "se-test", "class": "test_class"},
        "scope": {"includes": ["something"], "excludes": []},
    }


def test_own_manifest_is_valid() -> None:
    """The shipped SE_MANIFEST.toml must conform to the schema."""
    manifest = load_manifest()
    schema = cast(ManifestSchemaData, load_schema())
    errors = validate_manifest(manifest, schema)
    assert errors == [], "\n".join(errors)


def test_valid_manifest_passes() -> None:
    errors = validate_manifest(_minimal_manifest(), _minimal_schema())
    assert errors == []


def test_missing_required_section_detected() -> None:
    manifest = _minimal_manifest()
    del manifest["scope"]
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("scope" in e for e in errors)


def test_forbidden_section_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            **_minimal_schema(),
            "class": {
                "test_class": {
                    "required_sections": ["repo", "scope"],
                    "optional_sections": [],
                    "forbidden_sections": ["scope"],
                }
            },
        },
    )
    errors = validate_manifest(_minimal_manifest(), schema)
    assert any("forbids" in e for e in errors)


def test_unknown_section_detected() -> None:
    manifest = _minimal_manifest()
    manifest["surprise"] = {"key": "value"}
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("surprise" in e for e in errors)


def test_unknown_field_detected() -> None:
    manifest = _minimal_manifest()
    manifest["repo"]["unknown_field"] = "value"
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("unknown_field" in e for e in errors)


def test_invalid_schema_value_detected() -> None:
    manifest = _minimal_manifest()
    manifest["schema"] = "wrong-schema"
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("wrong-schema" in e for e in errors)


def test_missing_schema_url_detected() -> None:
    manifest = _minimal_manifest()
    del manifest["schema_url"]
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("schema_url" in e for e in errors)


def test_unknown_class_detected() -> None:
    manifest = _minimal_manifest()
    manifest["repo"]["class"] = "nonexistent"
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("nonexistent" in e for e in errors)


def test_missing_repo_section_detected() -> None:
    manifest = _minimal_manifest()
    del manifest["repo"]
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("repo" in e for e in errors)
