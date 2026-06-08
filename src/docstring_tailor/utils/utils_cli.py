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


def show_diff(original: str, modified: str, path: Path) -> None:
    """Prints a unified diff between the original and modified source to stdout.

    Skips output entirely if the two sources are identical. Each line of the diff is coloured:
    additions in green, removals in red, and header lines in bold, falling back to plain output on
    terminals that don't support ANSI codes.

    Args:
        original (str): The source text before formatting.
        modified (str): The source text after formatting.
        path (Path): The file path, used as the diff header label.
    """
    if original == modified:
        return

    diff_lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile=f"{path} (original)",
        tofile=f"{path} (formatted)",
    )

    for line in diff_lines:
        if line.startswith("+++") or line.startswith("---"):
            typer.echo(typer.style(line, bold=True), nl=False)
        elif line.startswith("+"):
            typer.echo(typer.style(line, fg=typer.colors.GREEN), nl=False)
        elif line.startswith("-"):
            typer.echo(typer.style(line, fg=typer.colors.RED), nl=False)
        else:
            typer.echo(line, nl=False)
