"""Tests for validation/validate_role_capability_map.py."""

from pathlib import Path
from typing import Any

from se_manifest_schema.validation.validate_role_capability_map import (
    validate_role_capability_map_data,
    validate_role_capability_map_file,
)

# ── helpers ────────────────────────────────────────────────────────────────────


def _minimal_valid_data() -> dict[str, Any]:
    """Return a minimal valid role-capability-map data dict."""
    return {
        "schema": {
            "schema_id": "se-role-capability-map-1",
            "version": "0.1.0",
            "status": "draft",
            "title": "SE Role Capability Map",
            "description": "Maps manifest classes to role groups.",
        },
        "export": {
            "path": "data/schema/role-capability-map.toml",
            "schema_path": "data/schema/role-capability-map.schema.toml",
        },
        "consumers": {
            "graph_verifier": "se-manifest verify-graph",
            "stage_verifier": "accountable-record",
            "future_rust_verifier": "accountable-record-rs",
        },
        "role_groups": {
            "core": "core_group",
            "contract": "contract_group",
        },
        "capability_profiles": {
            "core_group": {
                "validates_target_materials": False,
                "validates_resolution": False,
                "requires_lock_artifact": False,
                "exports_contract_artifacts": False,
                "emits_human_reports": False,
            },
            "contract_group": {
                "validates_target_materials": True,
                "validates_resolution": True,
                "requires_lock_artifact": False,
                "exports_contract_artifacts": True,
                "emits_human_reports": True,
            },
        },
        "graph_permissions": {
            "semantic_edge_kinds": ["semantic"],
            "resolution_checked_edge_kinds": ["semantic"],
            "entry_point_role_groups": ["core_group"],
            "no_core_depends_on_domain": {
                "diagnostic": "SE.ORG.LAYER_VIOLATION",
                "source_role_groups": ["core_group"],
                "forbidden_target_role_groups": ["contract_group"],
            },
            "no_interpretation_leak": {
                "diagnostic": "SE.ORG.INTERPRETATION_LEAK",
                "source_role_groups": ["core_group"],
                "forbidden_target_role_groups": ["contract_group"],
            },
            "no_contract_depends_on_implementation": {
                "diagnostic": "SE.ORG.CONTRACT_IMPL_DEP",
                "source_role_groups": ["contract_group"],
                "forbidden_target_role_groups": ["core_group"],
            },
            "no_theory_bypass": {
                "diagnostic": "SE.ORG.THEORY_BYPASS",
                "source_role_groups": ["core_group"],
                "forbidden_target_role_groups": ["contract_group"],
                "allowed_intermediate_role_groups": ["contract_group"],
            },
            "layer_monotonicity": {
                "diagnostic": "SE.ORG.LAYER_MONOTONICITY",
                "uses_layer_order": True,
            },
        },
        "layer_order": {
            "core_group": 1,
            "contract_group": 2,
        },
        "surface_buckets": {
            "required": ["types", "predicates", "axioms", "theorems", "witnesses"],
            "constant_names": [
                "SURFACE_TYPES",
                "SURFACE_PREDICATES",
                "SURFACE_AXIOMS",
                "SURFACE_THEOREMS",
                "SURFACE_WITNESSES",
            ],
        },
    }


# ── validate_role_capability_map_file ─────────────────────────────────────────


def test_file_not_found_returns_error(tmp_path: Path) -> None:
    path = tmp_path / "missing.toml"
    errors = validate_role_capability_map_file(path)
    assert any("does not exist" in e for e in errors)


def test_file_valid_returns_no_errors() -> None:
    project_root = Path(__file__).parent.parent
    real_path = project_root / "data" / "schema" / "role-capability-map.toml"

    if real_path.exists():
        errors = validate_role_capability_map_file(real_path)
        assert errors == [], "\n".join(errors)


# ── validate_role_capability_map_data ─────────────────────────────────────────


def test_valid_data_returns_no_errors() -> None:
    errors = validate_role_capability_map_data(_minimal_valid_data())
    assert errors == [], "\n".join(errors)


def test_missing_top_level_section_detected() -> None:
    data = _minimal_valid_data()
    del data["schema"]
    errors = validate_role_capability_map_data(data)
    assert any("schema" in e for e in errors)


def test_multiple_missing_sections_all_reported() -> None:
    # Removing two required sections should produce two distinct error messages.
    data = _minimal_valid_data()
    del data["schema"]
    del data["export"]
    errors = validate_role_capability_map_data(data)
    assert any("schema" in e for e in errors)
    assert any("export" in e for e in errors)


def test_missing_schema_field_detected() -> None:
    data = _minimal_valid_data()
    del data["schema"]["title"]
    errors = validate_role_capability_map_data(data)
    assert any("schema.title" in e for e in errors)


def test_empty_schema_field_detected() -> None:
    data = _minimal_valid_data()
    data["schema"]["title"] = ""
    errors = validate_role_capability_map_data(data)
    assert any("schema.title" in e for e in errors)


def test_missing_export_field_detected() -> None:
    data = _minimal_valid_data()
    del data["export"]["path"]
    errors = validate_role_capability_map_data(data)
    assert any("export.path" in e for e in errors)


def test_missing_consumer_field_detected() -> None:
    data = _minimal_valid_data()
    del data["consumers"]["graph_verifier"]
    errors = validate_role_capability_map_data(data)
    assert any("consumers.graph_verifier" in e for e in errors)


def test_empty_role_groups_detected() -> None:
    data = _minimal_valid_data()
    data["role_groups"] = {}
    errors = validate_role_capability_map_data(data)
    assert any("role_groups" in e for e in errors)


def test_non_string_role_group_value_detected() -> None:
    data = _minimal_valid_data()
    data["role_groups"]["core"] = 42
    errors = validate_role_capability_map_data(data)
    assert any("role_groups.core" in e for e in errors)


def test_missing_capability_profile_detected() -> None:
    data = _minimal_valid_data()
    del data["capability_profiles"]["core_group"]
    errors = validate_role_capability_map_data(data)
    assert any("capability_profiles.core_group" in e for e in errors)


def test_non_bool_capability_field_detected() -> None:
    data = _minimal_valid_data()
    data["capability_profiles"]["core_group"]["validates_target_materials"] = "yes"
    errors = validate_role_capability_map_data(data)
    assert any("validates_target_materials" in e for e in errors)


def test_missing_graph_permission_list_field_detected() -> None:
    data = _minimal_valid_data()
    del data["graph_permissions"]["semantic_edge_kinds"]
    errors = validate_role_capability_map_data(data)
    assert any("semantic_edge_kinds" in e for e in errors)


def test_non_list_graph_permission_field_detected() -> None:
    data = _minimal_valid_data()
    data["graph_permissions"]["entry_point_role_groups"] = "not-a-list"
    errors = validate_role_capability_map_data(data)
    assert any("entry_point_role_groups" in e for e in errors)


def test_missing_graph_rule_detected() -> None:
    data = _minimal_valid_data()
    del data["graph_permissions"]["no_core_depends_on_domain"]
    errors = validate_role_capability_map_data(data)
    assert any("no_core_depends_on_domain" in e for e in errors)


def test_graph_rule_missing_diagnostic_detected() -> None:
    data = _minimal_valid_data()
    del data["graph_permissions"]["no_core_depends_on_domain"]["diagnostic"]
    errors = validate_role_capability_map_data(data)
    assert any("no_core_depends_on_domain.diagnostic" in e for e in errors)


def test_graph_rule_diagnostic_must_start_with_se_org() -> None:
    data = _minimal_valid_data()
    data["graph_permissions"]["no_core_depends_on_domain"]["diagnostic"] = "WRONG.CODE"
    errors = validate_role_capability_map_data(data)
    assert any("no_core_depends_on_domain.diagnostic" in e for e in errors)


def test_forbidden_edge_rule_source_groups_detected() -> None:
    data = _minimal_valid_data()
    data["graph_permissions"]["no_core_depends_on_domain"]["source_role_groups"] = "bad"
    errors = validate_role_capability_map_data(data)
    assert any("source_role_groups" in e for e in errors)


def test_forbidden_edge_rule_target_groups_detected() -> None:
    data = _minimal_valid_data()
    data["graph_permissions"]["no_core_depends_on_domain"][
        "forbidden_target_role_groups"
    ] = "bad"
    errors = validate_role_capability_map_data(data)
    assert any("forbidden_target_role_groups" in e for e in errors)


def test_theory_bypass_allowed_intermediates_detected() -> None:
    data = _minimal_valid_data()
    data["graph_permissions"]["no_theory_bypass"][
        "allowed_intermediate_role_groups"
    ] = "bad"
    errors = validate_role_capability_map_data(data)
    assert any("allowed_intermediate_role_groups" in e for e in errors)


def test_layer_monotonicity_uses_layer_order_must_be_true() -> None:
    data = _minimal_valid_data()
    data["graph_permissions"]["layer_monotonicity"]["uses_layer_order"] = False
    errors = validate_role_capability_map_data(data)
    assert any("uses_layer_order" in e for e in errors)


def test_missing_layer_order_entry_detected() -> None:
    data = _minimal_valid_data()
    del data["layer_order"]["core_group"]
    errors = validate_role_capability_map_data(data)
    assert any("layer_order.core_group" in e for e in errors)


def test_non_int_layer_order_detected() -> None:
    data = _minimal_valid_data()
    data["layer_order"]["core_group"] = "first"
    errors = validate_role_capability_map_data(data)
    assert any("layer_order.core_group" in e for e in errors)


def test_wrong_surface_buckets_required_detected() -> None:
    data = _minimal_valid_data()
    data["surface_buckets"]["required"] = ["types", "predicates"]
    errors = validate_role_capability_map_data(data)
    assert any("surface_buckets.required" in e for e in errors)


def test_wrong_surface_buckets_constant_names_detected() -> None:
    data = _minimal_valid_data()
    data["surface_buckets"]["constant_names"] = ["WRONG"]
    errors = validate_role_capability_map_data(data)
    assert any("surface_buckets.constant_names" in e for e in errors)
