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


def test_manifest_filename_allowed_accepts_se_manifest() -> None:
    errors = validate_manifest(
        _minimal_manifest(),
        _minimal_schema(),
        manifest_filename="SE_MANIFEST.toml",
    )
    assert errors == []


def test_manifest_filename_allowed_accepts_manifest() -> None:
    schema = _minimal_schema()
    manifest_schema = cast(dict[str, Any], schema.setdefault("manifest", {}))
    manifest_schema["filename"] = "SE_MANIFEST.toml"
    manifest_schema["allowed_filenames"] = ["SE_MANIFEST.toml", "MANIFEST.toml"]
    manifest_schema["require_manifest_filename_allowed"] = True

    errors = validate_manifest(
        _minimal_manifest(),
        schema,
        manifest_filename="MANIFEST.toml",
    )

    assert errors == []


def test_manifest_filename_allowed_rejects_unknown_filename() -> None:
    schema = _minimal_schema()

    manifest_table = cast(dict[str, Any], schema.setdefault("manifest", {}))
    manifest_table["filename"] = "SE_MANIFEST.toml"
    manifest_table["allowed_filenames"] = ["SE_MANIFEST.toml", "MANIFEST.toml"]

    validation_table = cast(dict[str, Any], schema.setdefault("validation", {}))
    validation_table["require_manifest_filename_allowed"] = True

    errors = validate_manifest(
        _minimal_manifest(),
        schema,
        manifest_filename="BAD.toml",
    )

    assert any("BAD.toml" in error for error in errors)


def test_manifest_filename_exact_rejects_noncanonical_filename() -> None:
    schema = _minimal_schema()

    manifest_table = cast(dict[str, Any], schema.setdefault("manifest", {}))
    manifest_table["filename"] = "SE_MANIFEST.toml"

    validation_table = cast(dict[str, Any], schema.setdefault("validation", {}))
    validation_table["require_manifest_filename_exact"] = True

    errors = validate_manifest(
        _minimal_manifest(),
        schema,
        manifest_filename="MANIFEST.toml",
    )

    assert any("required filename" in error for error in errors)


def test_contract_authority_manifest_passes() -> None:
    errors = validate_manifest(_authority_manifest(), _contract_schema())
    assert errors == []


def test_domain_contract_manifest_passes() -> None:
    errors = validate_manifest(_domain_contract_manifest(), _contract_schema())
    assert errors == []


def test_contract_role_must_be_known() -> None:
    manifest = _authority_manifest()
    manifest["contract"]["contract_role"] = "bad-role"

    errors = validate_manifest(manifest, _contract_schema())

    assert any("allowed contract roles" in error for error in errors)


def test_contract_role_required_for_contract_class() -> None:
    manifest = _authority_manifest()
    del manifest["contract"]["contract_role"]

    errors = validate_manifest(manifest, _contract_schema())

    assert any("contract_role" in error for error in errors)


def test_contract_authority_required_for_contract_class() -> None:
    manifest = _authority_manifest()
    del manifest["contract"]["contract_authority"]

    errors = validate_manifest(manifest, _contract_schema())

    assert any("contract_authority" in error for error in errors)


def test_contract_version_required_for_contract_class() -> None:
    manifest = _authority_manifest()
    del manifest["contract"]["contract_version"]

    errors = validate_manifest(manifest, _contract_schema())

    assert any("contract_version" in error for error in errors)


def test_contract_authority_must_equal_repo_name() -> None:
    manifest = _authority_manifest()
    manifest["contract"]["contract_authority"] = "other-contract"

    errors = validate_manifest(manifest, _contract_schema())

    assert any("must equal [repo].name" in error for error in errors)


def test_authority_role_must_not_consume_contract() -> None:
    manifest = _authority_manifest()
    manifest["contract"]["consumes_contract_from"] = "upstream-contract"

    errors = validate_manifest(manifest, _contract_schema())

    assert any("must be absent" in error for error in errors)


def test_domain_contract_role_must_consume_contract() -> None:
    manifest = _domain_contract_manifest()
    del manifest["contract"]["consumes_contract_from"]

    errors = validate_manifest(manifest, _contract_schema())

    assert any(
        "required for contract_role 'domain-contract'" in error for error in errors
    )


def test_domain_contract_must_not_consume_self() -> None:
    manifest = _domain_contract_manifest()
    manifest["contract"]["consumes_contract_from"] = "judicial-record"

    errors = validate_manifest(manifest, _contract_schema())

    assert any("must not consume itself" in error for error in errors)


def test_non_contract_class_skips_contract_rules() -> None:
    manifest = _minimal_manifest()
    schema = _minimal_schema()
    validation_schema = cast(dict[str, Any], schema.setdefault("validation", {}))
    validation_schema["contract"] = {
        "contract_role_required_for_contract_class": True,
    }

    errors = validate_manifest(manifest, schema)

    assert errors == []


def test_contract_class_missing_contract_section_reports_required_section() -> None:
    manifest = _authority_manifest()
    del manifest["contract"]

    errors = validate_manifest(manifest, _contract_schema())

    assert any("requires section '[contract]'" in error for error in errors)


def _authority_manifest() -> dict[str, Any]:
    return {
        "schema": "se-manifest-2",
        "schema_url": "https://example.com",
        "repo": {"name": "accountable-record", "class": "contract"},
        "contract": {
            "contract_role": "authority",
            "contract_authority": "accountable-record",
            "contract_version": "1.2.3",
        },
    }


def _contract_schema() -> ManifestSchemaData:
    return cast(
        ManifestSchemaData,
        {
            "manifest": {
                "identity": {
                    "schema_required": True,
                    "schema_allowed": ["se-manifest-2"],
                    "schema_url_required": True,
                },
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "section": {
                "repo": {"required": True, "allowed_fields": ["name", "class"]},
                "contract": {
                    "required": True,
                    "allowed_fields": [
                        "contract_role",
                        "contract_authority",
                        "contract_version",
                        "consumes_contract_from",
                    ],
                },
            },
            "field": {
                "repo": {
                    "name": {"type": "string", "required": True},
                    "class": {"type": "string", "required": True},
                },
                "contract": {
                    "contract_role": {
                        "type": "string",
                        "required": False,
                        "constraints": ["known-contract-role"],
                    },
                    "contract_authority": {"type": "string", "required": False},
                    "contract_version": {"type": "string", "required": False},
                    "consumes_contract_from": {"type": "string", "required": False},
                },
            },
            "class": {
                "contract": {
                    "required_sections": ["repo", "contract"],
                    "optional_sections": [],
                    "forbidden_sections": [],
                }
            },
            "contract_roles": {
                "allowed": ["authority", "domain-contract"],
            },
            "validation": {
                "require_known_sections_only": True,
                "require_known_fields_only": True,
                "require_manifest_filename_allowed": True,
                "contract": {
                    "contract_role_required_for_contract_class": True,
                    "contract_authority_required_for_contract_class": True,
                    "contract_version_required_for_contract_class": True,
                    "contract_role_must_be_known": True,
                    "contract_authority_must_equal_self": True,
                    "authority_role_must_not_consume_contract": True,
                    "domain_contract_role_must_consume_contract": True,
                    "domain_contract_must_not_consume_self": True,
                },
            },
        },
    )


def _domain_contract_manifest() -> dict[str, Any]:
    return {
        "schema": "se-manifest-2",
        "schema_url": "https://example.com",
        "repo": {"name": "judicial-record", "class": "contract"},
        "contract": {
            "contract_role": "domain-contract",
            "contract_authority": "judicial-record",
            "contract_version": "1.2.3",
            "consumes_contract_from": "accountable-record",
        },
    }


# ── additional branch coverage ─────────────────────────────────────────────────


def test_missing_repo_class_string_detected() -> None:
    manifest = _minimal_manifest()
    manifest["repo"] = {"name": "se-test"}  # class missing entirely
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("[repo].class" in e for e in errors)


def test_missing_repo_name_string_detected() -> None:
    manifest = _minimal_manifest()
    manifest["repo"] = {"class": "test_class"}  # name missing
    errors = validate_manifest(manifest, _minimal_schema())
    assert any("[repo].name" in e for e in errors)


def test_required_field_missing_in_section_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            **_minimal_schema(),
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
        },
    )
    manifest = _minimal_manifest()
    del manifest["scope"]["includes"]
    errors = validate_manifest(manifest, schema)
    assert any("includes" in e and "required field missing" in e for e in errors)


def test_section_with_no_definition_is_skipped_without_require_known() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            **_minimal_schema(),
            "validation": {
                "require_known_sections_only": False,
                "require_known_fields_only": False,
            },
        },
    )
    manifest = _minimal_manifest()
    manifest["extra_section"] = {"key": "value"}
    errors = validate_manifest(manifest, schema)
    # extra_section has no definition, so it should be silently skipped
    assert all("extra_section" not in e for e in errors)


def test_contract_section_non_dict_skips_contract_rules() -> None:
    manifest = _authority_manifest()
    manifest["contract"] = "not-a-dict"
    # Replace schema so contract section is optional (won't fail on required section)
    schema = cast(
        ManifestSchemaData,
        {
            **_contract_schema(),
            "class": {
                "contract": {
                    "required_sections": ["repo"],
                    "optional_sections": ["contract"],
                    "forbidden_sections": [],
                }
            },
        },
    )
    errors = validate_manifest(manifest, schema)
    # contract_role rules should be skipped; no contract_role error expected
    assert not any("contract_role" in e for e in errors)


def test_field_constraint_unknown_role_detected() -> None:
    manifest = _authority_manifest()
    manifest["contract"]["contract_role"] = "unknown-role"
    errors = validate_manifest(manifest, _contract_schema())
    assert any("allowed contract roles" in e for e in errors)
