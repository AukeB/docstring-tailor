"""Module containing various utility functions."""

from pathlib import Path

import typer


def load_config() -> dict:
    """
    Loads configuration from docstring_tailor.toml or pyproject.toml.

    Walks up from the current directory. docstring_tailor.toml takes priority
    over pyproject.toml if both exist at the same level. Stops at the first
    file found containing docstring_tailor configuration.

    Returns:
        config (dict): Configuration settings, or an empty dict if none found.
    """
    import tomllib

    for directory in [Path.cwd(), *Path.cwd().parents]:
        tailor_config = directory / "docstring_tailor.toml"
        if tailor_config.exists():
            with open(tailor_config, "rb") as file:
                return tomllib.load(file)

        pyproject = directory / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject, "rb") as file:
                data = tomllib.load(file)
            tool_config = data.get("tool", {}).get("docstring_tailor", {})
            if tool_config:
                return tool_config

    return {}


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
