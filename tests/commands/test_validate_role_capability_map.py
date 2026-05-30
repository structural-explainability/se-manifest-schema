"""Tests for commands/validate_role_capability_map.py."""

from pathlib import Path
from typing import Any
from unittest.mock import patch

from se_manifest_schema.commands.validate_role_capability_map import run


def test_run_returns_0_when_valid(tmp_path: Path) -> None:
    with patch(
        "se_manifest_schema.commands.validate_role_capability_map.validate_role_capability_map_file",
        return_value=[],
    ):
        result = run(path=tmp_path / "role-capability-map.toml")
    assert result == 0


def test_run_returns_1_when_errors(tmp_path: Path) -> None:
    with patch(
        "se_manifest_schema.commands.validate_role_capability_map.validate_role_capability_map_file",
        return_value=["schema.title: must be a nonempty string"],
    ):
        result = run(path=tmp_path / "role-capability-map.toml")
    assert result == 1


def test_run_against_real_file_returns_0() -> None:
    project_root = Path(__file__).parent.parent.parent
    real_path = project_root / "data" / "schema" / "role-capability-map.toml"
    if real_path.exists():
        result = run(path=real_path)
        assert result == 0
