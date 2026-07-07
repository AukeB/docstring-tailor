"""Module containing various utility functions related to interacting with local
file system.
"""

from pathlib import Path

import typer


def load_config() -> dict:
    """Loads configuration from docstring_tailor.toml or pyproject.toml.

    Walks up from the current directory. docstring_tailor.toml takes priority
    over pyproject.toml if both exist at the same level. Stops at the first file
    found containing docstring_tailor configuration.

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


def _is_excluded(path: Path, exclude_patterns: list[str], project_root: Path) -> bool:
    """Checks whether a path matches any of the provided exclusion patterns.

    - Supports two pattern types, mirroring Ruff's exclude behaviour:
    - Single-path patterns (e.g. '.mypy_cache', 'foo.py', 'foo_*.py') are
      matched against every component of the path, so they exclude by name
      anywhere in the tree.
    - Relative patterns containing a separator (e.g. 'directory/foo.py',
      'directory/*.py') are matched against the path relative to the project
      root, so they only exclude at that specific location.

    Args:
        path (Path): The absolute path to test.
        exclude_patterns (list[str]): Glob patterns provided via --exclude.
        project_root (Path): The directory against which relative patterns are
            resolved (typically cwd or the directory containing pyproject.toml).

    Returns:
        excluded (bool): True if the path matches at least one pattern.
    """
    for pattern in exclude_patterns:
        is_relative_pattern = "/" in pattern or "\\" in pattern
        if is_relative_pattern:
            try:
                relative_path = path.relative_to(project_root)
                if relative_path.match(pattern):
                    return True
            except ValueError:
                pass
        else:
            for part in path.parts:
                if Path(part).match(pattern):
                    return True

    return False


def collect_python_files(
    paths: list[Path],
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """Collects all Python files from a list of file and/or directory paths.

    Directories are searched recursively. Files are included directly. Any path
    matching one of the provided exclusion patterns is silently skipped.

    Args:
        paths (list[Path]): A list of file and/or directory paths to search.
        exclude_patterns (list[str] | None): Glob patterns for paths to exclude.

    Returns:
        python_files (list[Path]): A flat list of all collected .py file paths.
    """
    resolved_patterns = exclude_patterns or []
    project_root = Path.cwd()
    python_files: list[Path] = []

    for path in paths:
        if path.is_dir():
            for candidate in path.rglob("*.py"):
                if not _is_excluded(candidate, resolved_patterns, project_root):
                    python_files.append(candidate)
        else:
            if not _is_excluded(path, resolved_patterns, project_root):
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
