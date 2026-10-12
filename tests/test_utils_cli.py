"""Tests for the CLI helper functions in ``utils_cli``."""

from pathlib import Path

import pytest
import typer

from docstring_tailor.utils.utils_cli import (
    _style_diff_line,
    show_diff,
    version_callback,
)

# Testing the "version_callback" function.


def test_version_callback_does_nothing_when_the_flag_is_absent() -> None:
    """Checks that no output is produced and the run continues when -V is not passed."""
    version_callback(False)


def test_version_callback_prints_the_version_and_exits(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Checks that passing -V prints a version string and raises typer.Exit."""
    with pytest.raises(typer.Exit):
        version_callback(True)

    assert capsys.readouterr().out.strip() != ""


# Testing the "_style_diff_line" function.


@pytest.mark.parametrize(
    ("line", "expected_text"),
    [
        ("--- a.py (original)\n", "--- a.py (original)\n"),
        ("+++ a.py (formatted)\n", "+++ a.py (formatted)\n"),
        ("+added line\n", "+added line\n"),
        ("-removed line\n", "-removed line\n"),
        (" context line\n", " context line\n"),
    ],
)
def test_style_diff_line_keeps_the_text_of_every_line_kind(
    line: str, expected_text: str
) -> None:
    """Checks that each kind of diff line still contains its original text once styled."""
    styled = _style_diff_line(line=line)

    assert expected_text.strip() in styled


def test_style_diff_line_leaves_context_lines_unstyled() -> None:
    """Checks that context lines are returned without any ANSI styling."""
    line = " context line\n"

    assert _style_diff_line(line=line) == line


# Testing the "show_diff" function.


def test_show_diff_prints_nothing_for_identical_sources(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Checks that identical sources produce no diff output."""
    show_diff(original="x = 1\n", modified="x = 1\n", path=Path("module.py"))

    assert capsys.readouterr().out == ""


def test_show_diff_prints_a_unified_diff(capsys: pytest.CaptureFixture[str]) -> None:
    """Checks that differing sources produce a unified diff labelled with the path."""
    show_diff(original="x = 1\n", modified="x = 2\n", path=Path("module.py"))

    output = capsys.readouterr().out

    assert "module.py (original)" in output
    assert "module.py (formatted)" in output
    assert "+x = 2" in output
    assert "-x = 1" in output
