"""Tests for the file system helpers in ``utils_file_system``."""

from pathlib import Path

import pytest
import typer

from docstring_tailor.utils.utils_file_system import (
    _is_excluded,
    collect_python_files,
    load_config,
    validate_paths,
)


@pytest.fixture
def nested_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Creates a nested directory with no project configuration and changes into it.

    Args:
        tmp_path (Path): A fresh temporary directory provided by pytest.
        monkeypatch (pytest.MonkeyPatch): Used to change the working directory.

    Returns:
        nested_dir (Path): The innermost directory, now the working directory.
    """
    nested = tmp_path / "project" / "package"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    return nested


# Testing the "load_config" function.


def test_load_config_reads_docstring_tailor_toml(nested_dir: Path) -> None:
    """Checks that a docstring_tailor.toml file in the working directory is read."""
    (nested_dir / "docstring_tailor.toml").write_text(
        'style = "numpy"\n', encoding="utf-8"
    )

    config = load_config()

    assert config.get("style") == "numpy"


def test_load_config_reads_the_tool_table_of_pyproject(nested_dir: Path) -> None:
    """Checks that the docstring_tailor table of pyproject.toml is read."""
    (nested_dir / "pyproject.toml").write_text(
        "[tool.docstring_tailor]\nline-length = 88\n", encoding="utf-8"
    )

    config = load_config()

    assert config.get("line-length") == 88


def test_load_config_walks_up_past_a_pyproject_without_the_table(
    nested_dir: Path,
) -> None:
    """Checks that a pyproject.toml without docstring_tailor settings is skipped."""
    parent = nested_dir.parent
    (parent / "pyproject.toml").write_text("[tool.other]\nkey = 1\n", encoding="utf-8")
    (parent / "docstring_tailor.toml").write_text(
        'style = "sphinx"\n', encoding="utf-8"
    )
    (nested_dir / "pyproject.toml").write_text(
        '[project]\nname = "x"\n', encoding="utf-8"
    )

    config = load_config()

    assert config.get("style") == "sphinx"


def test_load_config_returns_an_empty_dict_when_nothing_is_configured(
    nested_dir: Path,
) -> None:
    """Checks that the defaults are used when no configuration file exists."""
    config = load_config()

    assert config == {}


# Testing the "_is_excluded" function.


def test_is_excluded_matches_a_bare_name_anywhere_in_the_tree(tmp_path: Path) -> None:
    """Checks that a single-path pattern excludes a matching component at any depth."""
    path = tmp_path / "deep" / "tests" / "test_x.py"

    assert _is_excluded(path, ["tests"], project_root=tmp_path)


def test_is_excluded_matches_a_relative_pattern_only_at_its_location(
    tmp_path: Path,
) -> None:
    """Checks that a pattern with a separator matches relative to the project root."""
    path = tmp_path / "src" / "generated" / "models.py"

    assert _is_excluded(path, ["src/generated/*.py"], project_root=tmp_path)
    assert not _is_excluded(path, ["other/generated/*.py"], project_root=tmp_path)


def test_is_excluded_ignores_relative_patterns_for_paths_outside_the_root(
    tmp_path: Path,
) -> None:
    """Checks that a relative pattern never matches a path outside the project root."""
    outside = tmp_path / "elsewhere" / "models.py"
    project_root = tmp_path / "project"

    assert not _is_excluded(outside, ["project/*.py"], project_root=project_root)


def test_is_excluded_returns_false_when_no_pattern_matches(tmp_path: Path) -> None:
    """Checks that a path is kept when no pattern matches it."""
    assert not _is_excluded(tmp_path / "module.py", ["tests"], project_root=tmp_path)


# Testing the "collect_python_files" function.


def test_collect_python_files_searches_directories_recursively(
    nested_dir: Path,
) -> None:
    """Checks that every .py file below a directory is collected, and nothing else."""
    (nested_dir / "a.py").write_text("", encoding="utf-8")
    (nested_dir / "sub").mkdir()
    (nested_dir / "sub" / "b.py").write_text("", encoding="utf-8")
    (nested_dir / "notes.txt").write_text("", encoding="utf-8")

    files = collect_python_files(paths=[nested_dir])

    assert sorted(path.name for path in files) == ["a.py", "b.py"]


def test_collect_python_files_applies_exclude_patterns(nested_dir: Path) -> None:
    """Checks that excluded files are left out of a directory search."""
    (nested_dir / "keep.py").write_text("", encoding="utf-8")
    (nested_dir / "drop.py").write_text("", encoding="utf-8")

    files = collect_python_files(paths=[nested_dir], exclude_patterns=["drop.py"])

    assert [path.name for path in files] == ["keep.py"]


def test_collect_python_files_includes_a_file_path_directly(nested_dir: Path) -> None:
    """Checks that a single file given on the command line is collected as is."""
    target = nested_dir / "single.py"
    target.write_text("", encoding="utf-8")

    files = collect_python_files(paths=[target])

    assert files == [target]


def test_collect_python_files_skips_an_excluded_file_path(nested_dir: Path) -> None:
    """Checks that a single file given on the command line is dropped when excluded."""
    target = nested_dir / "single.py"
    target.write_text("", encoding="utf-8")

    files = collect_python_files(paths=[target], exclude_patterns=["single.py"])

    assert files == []


# Testing the "validate_paths" function.


def test_validate_paths_accepts_existing_paths(nested_dir: Path) -> None:
    """Checks that existing paths pass validation without error."""
    validate_paths(paths=[nested_dir])


def test_validate_paths_exits_for_a_missing_path(nested_dir: Path) -> None:
    """Checks that a missing path stops the run with typer.Exit."""
    with pytest.raises(typer.Exit):
        validate_paths(paths=[nested_dir / "missing.py"])
