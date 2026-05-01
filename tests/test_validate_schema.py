"""test_validate_schema.py.

Tests for validate_schema.py and internal consistency of schema definitions.
"""

from typing import cast

from se_manifest_schema.types.manifest_schema import ManifestSchemaData
from se_manifest_schema.validate_schema import validate_schema_internal


def test_unknown_section_in_class_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"meta": {"allowed_fields": []}},
            "field": {},
            "class": {"fake": {"required_sections": ["meta", "nonexistent"]}},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("nonexistent" in e for e in errors)


def test_missing_field_definition_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"repo": {"allowed_fields": ["name"]}},
            "field": {"repo": {}},
            "class": {},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("repo.name" in e for e in errors)


def test_unknown_field_type_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"repo": {"allowed_fields": ["name"]}},
            "field": {"repo": {"name": {"type": "badtype", "required": True}}},
            "class": {},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("badtype" in e for e in errors)
