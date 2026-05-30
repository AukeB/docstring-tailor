"""Module containing various utility functions."""

from pathlib import Path

import typer


def collect_python_files(paths: list[Path]) -> list[Path]:
    """Collects all Python files from a list of file and/or directory paths.

    Directories are searched recursively. Files are included directly.

    Args:
        paths (list[Path]): A list of file and/or directory paths to search.

    Returns:
        python_files (list[Path]): A flat list of all collected .py file paths.
    """
    python_files: list[Path] = []
    for path in paths:
        if path.is_dir():
            python_files.extend(path.rglob("*.py"))
        else:
            python_files.append(path)

    return python_files


def validate_paths(paths: list[Path]) -> None:
    """Validates that all provided paths exist on the filesystem.

    Args:
        paths (list[Path]): A list of file and/or directory paths to validate.

    Raises:
        typer.Exit: If any path does not exist.
    """
    for path in paths:
        if not path.exists():
            typer.echo(f"Error: path '{path}' does not exist.")
            raise typer.Exit(code=1)
