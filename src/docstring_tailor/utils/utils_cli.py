"""Utility module containing helper functions for the CLI."""

import difflib
from importlib import metadata
from pathlib import Path

import typer


def version_callback(value: bool) -> None:
    """Print the package version and exit.

    Args:
        value (bool): Whether the flag was passed.

    Raises:
        typer.Exit: Always raised after printing, to halt execution.
    """

    if value:
        version = metadata.version("docstring-tailor")

        typer.echo(version)

        raise typer.Exit()


def _style_diff_line(line: str) -> str:
    """Applies colour to a single unified diff line based on its prefix.

    Header lines are bold, additions are green, removals are red, and all other
    lines are returned unchanged.

    Args:
        line (str): A single line of the unified diff.

    Returns:
        styled_line (str): The line with ANSI styling applied, or unchanged.
    """

    if line.startswith("+++") or line.startswith("---"):
        styled_line = typer.style(line, bold=True)
    elif line.startswith("+"):
        styled_line = typer.style(line, fg=typer.colors.GREEN)
    elif line.startswith("-"):
        styled_line = typer.style(line, fg=typer.colors.RED)
    else:
        styled_line = line

    return styled_line


def show_diff(original: str, modified: str, path: Path) -> None:
    """Prints a unified diff between the original and modified source to stdout.

    Skips output entirely if the two sources are identical. Each line of the
    diff is coloured: additions in green, removals in red, and header lines in
    bold, falling back to plain output on terminals that don't support ANSI
    codes.

    Args:
        original (str): The source text before formatting.
        modified (str): The source text after formatting.
        path (Path): The file path, used as the diff header label.
    """

    if original == modified:
        return

    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)

    diff_lines = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"{path} (original)",
        tofile=f"{path} (formatted)",
    )

    for line in diff_lines:
        styled_line = _style_diff_line(line=line)

        typer.echo(styled_line, nl=False)
