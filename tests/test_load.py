"""Tests for load.py - file loading and parsing."""

from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest

from se_manifest_schema.load import (
    ALTERNATE_MANIFEST_FILE_NAME,
    CANONICAL_MANIFEST_FILE_NAME,
    find_manifest_path,
    get_git_tag,
    get_repo_version,
    load_manifest,
    load_schema,
    load_toml,
    packaged_schema_text,
    repo_root_schema_path,
    schema_text,
)


def test_get_git_tag_not_found() -> None:
    with (
        patch("shutil.which", return_value=None),
        pytest.raises(RuntimeError, match="git executable"),
    ):
        get_git_tag()


def test_get_repo_version_missing_repo() -> None:
    with pytest.raises(ValueError, match="repository"):
        get_repo_version({})


def test_get_repo_version_missing_version() -> None:
    with pytest.raises(ValueError, match="version"):
        get_repo_version({"repository": {"name": "x"}})


def test_get_repo_version_valid() -> None:
    manifest = {"repository": {"version": "0.2.0", "name": "x"}}
    assert get_repo_version(manifest) == "0.2.0"


def test_load_manifest_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="MANIFEST.toml"):
        load_manifest(tmp_path / "MANIFEST.toml")


def test_load_schema_found() -> None:
    text = schema_text()
    data = load_schema()

    assert text.strip()
    assert isinstance(data, dict)
    assert data


def test_load_toml_valid(tmp_path: Path) -> None:
    f = tmp_path / "test.toml"
    f.write_text('[meta]\nversion = "1.0.0"\n', encoding="utf-8")
    data = load_toml(f)
    assert data["meta"]["version"] == "1.0.0"


def test_get_git_tag_success() -> None:
    mock_output = b"v1.2.3\n"
    with (
        patch("shutil.which", return_value="/usr/bin/git"),
        patch("subprocess.check_output", return_value=mock_output),
    ):
        tag = get_git_tag()
    assert tag == "v1.2.3"


def test_get_git_tag_not_on_tagged_commit() -> None:
    with (
        patch("shutil.which", return_value="/usr/bin/git"),
        patch(
            "subprocess.check_output",
            side_effect=subprocess.CalledProcessError(128, "git"),
        ),
        pytest.raises(RuntimeError, match="tagged commit"),
    ):
        get_git_tag()


def test_find_manifest_path_finds_canonical(tmp_path: Path) -> None:
    (tmp_path / CANONICAL_MANIFEST_FILE_NAME).write_text(
        "[repository]\n", encoding="utf-8"
    )
    result = find_manifest_path(tmp_path)
    assert result.name == CANONICAL_MANIFEST_FILE_NAME


def test_find_manifest_path_finds_alternate(tmp_path: Path) -> None:
    (tmp_path / ALTERNATE_MANIFEST_FILE_NAME).write_text(
        "[repository]\n", encoding="utf-8"
    )
    result = find_manifest_path(tmp_path)
    assert result.name == ALTERNATE_MANIFEST_FILE_NAME


def test_find_manifest_path_prefers_canonical(tmp_path: Path) -> None:
    (tmp_path / CANONICAL_MANIFEST_FILE_NAME).write_text(
        "[repository]\n", encoding="utf-8"
    )
    (tmp_path / ALTERNATE_MANIFEST_FILE_NAME).write_text(
        "[repository]\n", encoding="utf-8"
    )
    result = find_manifest_path(tmp_path)
    assert result.name == CANONICAL_MANIFEST_FILE_NAME


def test_find_manifest_path_raises_when_none(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No supported manifest"):
        find_manifest_path(tmp_path)


def test_find_manifest_path_defaults_to_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / CANONICAL_MANIFEST_FILE_NAME).write_text(
        "[repository]\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    result = find_manifest_path()
    assert result.name == CANONICAL_MANIFEST_FILE_NAME


def test_load_manifest_finds_canonical_in_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / CANONICAL_MANIFEST_FILE_NAME).write_text(
        '[repository]\nname = "x"\n', encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    data = load_manifest()
    assert data["repository"]["name"] == "x"


def test_packaged_schema_text_returns_nonempty_string() -> None:
    # packaged_schema_text() reads from the installed wheel artifact; in an editable
    # (source-checkout) install the bundled copy may not be present.  Skip gracefully.
    try:
        text = packaged_schema_text()
    except FileNotFoundError:
        import pytest

        pytest.skip("manifest-schema.toml not bundled in editable install")
    assert isinstance(text, str)
    assert len(text) > 0


def test_repo_root_schema_path_returns_none_in_tmp(tmp_path: Path) -> None:
    result = repo_root_schema_path(tmp_path)
    assert result is None


def test_repo_root_schema_path_finds_schema_in_repo() -> None:
    # Run from actual repo root (the test itself runs inside the repo)
    repo_root = Path(__file__).parent.parent
    result = repo_root_schema_path(repo_root)
    assert result is not None
    assert result.name == "manifest-schema.toml"
