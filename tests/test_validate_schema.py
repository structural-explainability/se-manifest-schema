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
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("nonexistent" in error for error in errors)


def test_missing_field_definition_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"repo": {"allowed_fields": ["name"]}},
            "field": {"repo": {}},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("repo.name" in error for error in errors)


def test_unknown_field_type_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"repo": {"allowed_fields": ["name"]}},
            "field": {"repo": {"name": {"type": "badtype", "required": True}}},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("badtype" in error for error in errors)


def test_retired_exact_manifest_filename_rule_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {
                "require_manifest_filename_exact": True,
                "require_manifest_filename_allowed": True,
            },
        },
    )
    errors = validate_schema_internal(schema)
    assert any("require_manifest_filename_exact" in error for error in errors)


def test_missing_allowed_manifest_filename_rule_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("require_manifest_filename_allowed" in error for error in errors)


def test_manifest_filename_must_be_nonempty_string() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("manifest.filename" in error for error in errors)


def test_allowed_manifest_filenames_must_be_list() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": "SE_MANIFEST.toml",
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("manifest.allowed_filenames" in error for error in errors)


def test_allowed_manifest_filenames_must_include_canonical_filename() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("canonical manifest.filename" in error for error in errors)


def test_allowed_manifest_filenames_must_include_se_manifest() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "MANIFEST.toml",
                "allowed_filenames": ["MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("SE_MANIFEST.toml" in error for error in errors)


def test_allowed_manifest_filenames_must_include_manifest() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("MANIFEST.toml" in error for error in errors)


def test_contract_roles_registry_required_when_constraint_used() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {
                "contract": {
                    "contract_role": {
                        "type": "string",
                        "required": False,
                        "constraints": ["known-contract-role"],
                    }
                }
            },
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("contract_roles.allowed" in error for error in errors)


def test_contract_roles_registry_must_include_authority() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {
                "contract": {
                    "contract_role": {
                        "type": "string",
                        "required": False,
                        "constraints": ["known-contract-role"],
                    }
                }
            },
            "class": {},
            "contract_roles": {"allowed": ["domain-contract"]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("authority" in error for error in errors)


def test_contract_roles_registry_must_include_domain_contract() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {
                "contract": {
                    "contract_role": {
                        "type": "string",
                        "required": False,
                        "constraints": ["known-contract-role"],
                    }
                }
            },
            "class": {},
            "contract_roles": {"allowed": ["authority"]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("domain-contract" in error for error in errors)
