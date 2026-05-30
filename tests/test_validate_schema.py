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


# ── additional branch coverage ─────────────────────────────────────────────────


def test_allowed_manifest_filenames_with_empty_string_item_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml", ""],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("nonempty strings" in error for error in errors)


def test_contract_roles_with_empty_string_role_detected() -> None:
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
            "contract_roles": {"allowed": ["authority", "domain-contract", ""]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("nonempty strings" in error for error in errors)


def test_custom_type_missing_definition_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("custom_types.allowed" in error for error in errors)


def test_custom_type_kind_must_be_record() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "custom_type": {
                "dependency": {
                    "kind": "enum",  # wrong kind
                    "fields": "dependency_fields",
                }
            },
            "dependency_fields": {"allowed_fields": ["repo", "version"]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("kind" in error for error in errors)


def test_custom_type_fields_registry_missing_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "custom_type": {
                "dependency": {
                    "kind": "record",
                    "fields": "nonexistent_registry",
                }
            },
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("unknown field registry" in error for error in errors)


def test_custom_type_fields_missing_allowed_fields_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "custom_type": {
                "dependency": {
                    "kind": "record",
                    "fields": "dependency_fields",
                }
            },
            "dependency_fields": {},  # missing allowed_fields
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("allowed_fields" in error for error in errors)


def test_custom_type_with_missing_fields_key_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "custom_type": {
                "dependency": {
                    "kind": "record",
                    # "fields" key missing entirely
                }
            },
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("fields" in error for error in errors)


def test_is_known_type_list_primitive() -> None:
    from se_manifest_schema.validate_schema import is_known_type

    assert is_known_type("list[string]", set())
    assert is_known_type("list[integer]", set())
    assert is_known_type("list[boolean]", set())


def test_is_known_type_map_primitive() -> None:
    from se_manifest_schema.validate_schema import is_known_type

    assert is_known_type("map[string]", set())


def test_is_known_type_custom() -> None:
    from se_manifest_schema.validate_schema import is_known_type

    assert is_known_type("dependency", {"dependency"})
    assert not is_known_type("unknown", set())


def test_is_known_type_list_custom() -> None:
    from se_manifest_schema.validate_schema import is_known_type

    assert is_known_type("list[dependency]", {"dependency"})


def test_iter_field_definitions_collects_typed_nodes() -> None:
    from se_manifest_schema.validate_schema import iter_field_definitions

    fields = {
        "repo": {
            "name": {"type": "string", "required": True},
            "class": {"type": "string", "required": True},
        }
    }
    results = iter_field_definitions(fields)
    paths = {path for path, _ in results}
    assert "repo.name" in paths
    assert "repo.class" in paths


def test_class_with_optional_and_forbidden_sections_unknown_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"repo": {"allowed_fields": []}},
            "field": {},
            "class": {
                "myclass": {
                    "optional_sections": ["unknown-opt"],
                    "forbidden_sections": ["unknown-forb"],
                }
            },
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("unknown-opt" in error for error in errors)
    assert any("unknown-forb" in error for error in errors)
