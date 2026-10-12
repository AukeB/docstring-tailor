"""Tests for the ``docstring_tailor`` command line interface."""

import runpy
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

import docstring_tailor.main
from docstring_tailor.constants import DIR_PATH_TEST_FIXTURES
from docstring_tailor.main import app

runner = CliRunner()


@pytest.fixture
def work_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Runs each test from an empty directory, so no project config is picked up.

    Args:
        tmp_path (Path): A fresh temporary directory provided by pytest.
        monkeypatch (pytest.MonkeyPatch): Used to change the working directory.

    Returns:
        work_dir (Path): The temporary directory, now the working directory.
    """
    monkeypatch.chdir(tmp_path)

    return tmp_path


def _copy_fixture(relative_path: str, destination: Path) -> Path:
    """Copies a fixture file into a working directory.

    Args:
        relative_path (str): The fixture path relative to the fixtures directory.
        destination (Path): The file to create.

    Returns:
        destination (Path): The copied file.
    """
    shutil.copy(DIR_PATH_TEST_FIXTURES / relative_path, destination)

    return destination


# Testing the "format" command.


def test_format_rewrites_a_file_and_reports_the_summary(work_dir: Path) -> None:
    """Checks that format writes changes and prints a Ruff-style summary."""
    target = _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_wrong_input.py",
        work_dir / "module.py",
    )
    original = target.read_text(encoding="utf-8")

    result = runner.invoke(app, ["format", str(target), "--style", "google"])

    assert result.exit_code == 0
    assert target.read_text(encoding="utf-8") != original
    assert "1 file reformatted" in result.output


def test_format_leaves_an_already_formatted_file_untouched(work_dir: Path) -> None:
    """Checks that a formatted file is not rewritten and is reported as unchanged."""
    target = _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_80.py",
        work_dir / "module.py",
    )

    result = runner.invoke(
        app, ["format", str(target), "--style", "google", "--line-length", "80"]
    )

    assert result.exit_code == 0
    assert "1 file left unchanged" in result.output


def test_format_diff_prints_changes_and_fails_without_writing(work_dir: Path) -> None:
    """Checks that --diff prints a diff, exits 1 and leaves the file as it was."""
    target = _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_wrong_input.py",
        work_dir / "module.py",
    )
    original = target.read_text(encoding="utf-8")

    result = runner.invoke(app, ["format", str(target), "--style", "google", "--diff"])

    assert result.exit_code == 1
    assert "(original)" in result.output
    assert target.read_text(encoding="utf-8") == original


def test_format_diff_exits_zero_when_nothing_would_change(work_dir: Path) -> None:
    """Checks that --diff exits 0 and prints nothing for an already formatted file."""
    target = _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_80.py",
        work_dir / "module.py",
    )

    result = runner.invoke(app, ["format", str(target), "--style", "google", "--diff"])

    assert result.exit_code == 0
    assert result.output == ""


def test_format_reads_style_and_line_length_from_pyproject(work_dir: Path) -> None:
    """Checks that style and line-length fall back to the project configuration."""
    (work_dir / "pyproject.toml").write_text(
        '[tool.docstring_tailor]\nstyle = "google"\nline-length = 80\n',
        encoding="utf-8",
    )
    target = _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_wrong_input.py",
        work_dir / "module.py",
    )

    result = runner.invoke(app, ["format", str(target)])

    assert result.exit_code == 0
    assert target.read_text(encoding="utf-8") == DIR_PATH_TEST_FIXTURES.joinpath(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_80.py"
    ).read_text(encoding="utf-8")


def test_format_without_a_style_fails(work_dir: Path) -> None:
    """Checks that format refuses to run when no style is given or configured."""
    target = _copy_fixture(
        "google/docstring_elements/empty/empty_80.py", work_dir / "module.py"
    )

    result = runner.invoke(app, ["format", str(target)])

    assert result.exit_code == 1
    assert "Docstring style not specified" in result.output


def test_format_with_an_unsupported_style_fails(work_dir: Path) -> None:
    """Checks that an epydoc style, which has no parser yet, is rejected."""
    target = _copy_fixture(
        "google/docstring_elements/empty/empty_80.py", work_dir / "module.py"
    )

    result = runner.invoke(app, ["format", str(target), "--style", "epydoc"])

    assert result.exit_code == 1
    assert "not yet supported" in result.output


def test_format_with_a_missing_path_fails(work_dir: Path) -> None:
    """Checks that a path that does not exist is reported and fails the run."""
    result = runner.invoke(app, ["format", "missing.py", "--style", "google"])

    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_format_reports_an_unparseable_file_and_fails(work_dir: Path) -> None:
    """Checks that a file that is not valid Python is reported and fails the run."""
    target = work_dir / "broken.py"
    target.write_text('"""Unclosed docstring\n', encoding="utf-8")

    result = runner.invoke(app, ["format", str(target), "--style", "google"])

    assert result.exit_code == 1
    assert "is not valid Python" in result.output


def test_format_reports_a_file_that_is_not_utf8(work_dir: Path) -> None:
    """Checks that a file that cannot be decoded is reported and fails the run."""
    target = work_dir / "binary.py"
    target.write_bytes(b'"""\xff\xfe"""\n')

    result = runner.invoke(app, ["format", str(target), "--style", "google"])

    assert result.exit_code == 1
    assert "is not valid utf-8 text" in result.output


def test_format_over_a_directory_skips_excluded_files(work_dir: Path) -> None:
    """Checks that --exclude keeps matching files out of a directory run."""
    package = work_dir / "package"
    package.mkdir()
    _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_wrong_input.py",
        package / "kept.py",
    )
    excluded = _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_wrong_input.py",
        package / "skipped.py",
    )
    excluded_original = excluded.read_text(encoding="utf-8")

    result = runner.invoke(
        app, ["format", str(package), "--style", "google", "--exclude", "skipped.py"]
    )

    assert result.exit_code == 0
    assert "1 file reformatted" in result.output
    assert excluded.read_text(encoding="utf-8") == excluded_original


def test_format_reports_a_file_that_cannot_be_written(work_dir: Path) -> None:
    """Checks that a write failure is reported as an error line and fails the run."""
    target = _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_wrong_input.py",
        work_dir / "module.py",
    )
    target.chmod(0o444)

    result = runner.invoke(app, ["format", str(target), "--style", "google"])

    target.chmod(0o644)

    assert result.exit_code == 1
    assert "could not read or write" in result.output


# Testing the "convert" command.


def test_convert_writes_the_target_style(work_dir: Path) -> None:
    """Checks that convert rewrites a docstring in the requested style."""
    target = _copy_fixture(
        "convert/google_to_numpy/function_docstring_wrong_input.py",
        work_dir / "module.py",
    )

    result = runner.invoke(
        app,
        ["convert", str(target), "--from-style", "google", "--to-style", "numpy"],
    )

    assert result.exit_code == 0
    assert "Parameters" in target.read_text(encoding="utf-8")


def test_convert_with_the_same_style_fails(work_dir: Path) -> None:
    """Checks that convert refuses identical source and target styles."""
    target = _copy_fixture(
        "google/docstring_elements/empty/empty_80.py", work_dir / "module.py"
    )

    result = runner.invoke(
        app,
        ["convert", str(target), "--from-style", "google", "--to-style", "google"],
    )

    assert result.exit_code == 1
    assert "Use the 'format' command" in result.output


def test_convert_with_an_unsupported_style_fails(work_dir: Path) -> None:
    """Checks that convert rejects an unsupported source or target style."""
    target = _copy_fixture(
        "google/docstring_elements/empty/empty_80.py", work_dir / "module.py"
    )

    result = runner.invoke(
        app,
        ["convert", str(target), "--from-style", "epydoc", "--to-style", "google"],
    )

    assert result.exit_code == 1
    assert "not yet supported" in result.output


def test_convert_reports_a_file_it_cannot_parse(work_dir: Path) -> None:
    """Checks that convert reports an unparseable file and fails the run."""
    target = work_dir / "broken.py"
    target.write_text('"""Unclosed docstring\n', encoding="utf-8")

    result = runner.invoke(
        app,
        ["convert", str(target), "--from-style", "google", "--to-style", "numpy"],
    )

    assert result.exit_code == 1
    assert "is not valid Python" in result.output


# Testing the global options.


def test_version_flag_prints_the_package_version(work_dir: Path) -> None:
    """Checks that -V prints a version string and exits successfully."""
    result = runner.invoke(app, ["-V"])

    assert result.exit_code == 0
    assert result.output.strip() != ""


def test_format_summary_names_both_reformatted_and_unchanged_files(
    work_dir: Path,
) -> None:
    """Checks that a run with both kinds of file reports both counts."""
    _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_wrong_input.py",
        work_dir / "changed.py",
    )
    _copy_fixture(
        "google/docstring_elements/paragraph_one_line/paragraph_one_line_80.py",
        work_dir / "unchanged.py",
    )

    result = runner.invoke(
        app, ["format", str(work_dir), "--style", "google", "--line-length", "80"]
    )

    assert result.exit_code == 0
    assert "1 file reformatted, 1 file left unchanged" in result.output


def test_running_the_module_as_a_script_invokes_the_app(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Checks that the module's __main__ block starts the Typer app."""
    monkeypatch.setattr("sys.argv", ["docstring_tailor", "-V"])

    with pytest.raises(SystemExit):
        runpy.run_path(docstring_tailor.main.__file__, run_name="__main__")

    assert capsys.readouterr().out.strip() != ""
