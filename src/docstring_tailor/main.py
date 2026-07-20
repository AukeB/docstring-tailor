"""Main module

Todo

- Fix that for return section the variable name is optional.
- Fix that the program does not break if brackets can not be found for variable
  types.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Optional

import libcst as cst
import typer

from docstring_tailor.cli_config import (
    DEFAULT_PATHS,
    DEFAULT_STYLE,
    LINE_LENGTH_DEFAULT,
    LINE_LENGTH_MAX,
    LINE_LENGTH_MIN,
    SUPPORTED_STYLES,
    DocstringStyle,
)
from docstring_tailor.constants import ENCODING
from docstring_tailor.docstring_visitor import DocstringVisitor
from docstring_tailor.utils.utils_cli import show_diff, version_callback
from docstring_tailor.utils.utils_file_system import (
    collect_python_files,
    load_config,
    validate_paths,
)

app = typer.Typer()

# Options shared between the format and convert commands.
_PATHS_ARGUMENT = typer.Argument(
    help="Files or directories to process. Defaults to 'src/'."
)
_LINE_LENGTH_OPTION = typer.Option(
    "--line-length",
    help=f"Maximum line length. Must be between {LINE_LENGTH_MIN} and {LINE_LENGTH_MAX}.",
    min=LINE_LENGTH_MIN,
    max=LINE_LENGTH_MAX,
)
_EXCLUDE_OPTION = typer.Option(
    "--exclude",
    help=(
        "A glob pattern for paths to exclude. Can be passed multiple times. "
        "Single-path patterns (e.g. 'tests', '*.pyi') match by name anywhere "
        "in the tree. Relative patterns (e.g. 'src/generated/*.py') match "
        "against the path relative to the project root."
    ),
)
_DIFF_OPTION = typer.Option(
    "--diff",
    help="Show a diff of changes without modifying any files.",
)


@app.callback()
def app_callback(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "-V",
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
) -> None:
    """docstring_tailor formats and converts Python docstrings between styles.

    Serves as the Typer app-level callback, so --version works without a
    subcommand (e.g. 'docstring_tailor --version'). The actual version- printing
    logic runs via version_callback, invoked eagerly by Typer as soon as the
    flag is parsed, so this function's own body never needs to reference version
    directly.

    Args:
        version (bool | None): If passed, print the version and exit.
    """


def _validate_supported_style(style: DocstringStyle) -> None:
    """Validates that a style is currently supported.

    Args:
        style (DocstringStyle): The style to validate.

    Raises:
        typer.Exit: If style is not in SUPPORTED_STYLES.
    """
    if style not in SUPPORTED_STYLES:
        typer.echo(
            f"Style '{style.value}' is not yet supported. "
            f"Currently supported: {', '.join(s.value for s in SUPPORTED_STYLES)}."
        )
        raise typer.Exit(code=1)


def _resolve_common_options(
    paths: list[Path] | None,
    line_length: int | None,
    exclude: list[str] | None,
) -> tuple[list[Path], int, list[str], dict]:
    """Resolves paths, line_length, and exclude with priority: CLI argument >
    config file > built-in default.

    Also returns the raw file_config dict, so a caller needing additional config
    keys (e.g. 'style' in format_command) doesn't need to reload the config file
    itself.

    Args:
        paths (list[Path] | None): Files or directories to process, from the
            CLI.
        line_length (int | None): Line length override, from the CLI.
        exclude (list[str] | None): Exclude patterns, from the CLI.

    Returns:
        resolved (tuple[list[Path], int, list[str], dict]): resolved_paths,
            resolved_line_length, resolved_exclude, and file_config, in that
            order.
    """
    file_config = load_config()

    resolved_paths = paths or [Path(p) for p in DEFAULT_PATHS]
    resolved_line_length = line_length or file_config.get(
        "line-length", LINE_LENGTH_DEFAULT
    )
    resolved_exclude = exclude or file_config.get("exclude", [])

    return resolved_paths, resolved_line_length, resolved_exclude, file_config


def _process_files(
    python_files: list[Path],
    visitor_factory: Callable[[], DocstringVisitor],
    diff: bool,
) -> None:
    """Parses, transforms, and writes or diffs each collected Python file.

    A fresh DocstringVisitor is created per file via visitor_factory, since
    DocstringVisitor accumulates indentation state as it traverses a single
    file's CST and cannot be safely reused across files.

    Args:
        python_files (list[Path]): The collected files to process.
        visitor_factory (Callable[[], DocstringVisitor]): Builds a fresh
            DocstringVisitor for each file.
        diff (bool): If True, print a diff instead of writing files.
    """
    for file_path in python_files:
        print(file_path)
        input_data = file_path.read_text(encoding=ENCODING)
        input_tree = cst.parse_module(source=input_data)
        modified_tree = input_tree.visit(visitor_factory())

        modified_code = modified_tree.code

        if diff:
            show_diff(original=input_data, modified=modified_code, path=file_path)
        else:
            file_path.write_text(modified_code, encoding=ENCODING)


@app.command("format")
def format_command(
    paths: Annotated[list[Path] | None, _PATHS_ARGUMENT] = None,
    line_length: Annotated[int | None, _LINE_LENGTH_OPTION] = None,
    style: Annotated[
        DocstringStyle | None,
        typer.Option("--style", help="Docstring style to format to."),
    ] = None,
    exclude: Annotated[list[str] | None, _EXCLUDE_OPTION] = None,
    diff: Annotated[bool, _DIFF_OPTION] = False,
) -> None:
    """Formats Python docstrings in the given files or directories to the
    specified style.

    Processes all .py files found at the provided paths, reformatting their
    docstrings in place. Directories are searched recursively. Parses and
    renders in the same style, so no keyword translation is needed -- see
    convert_command for converting between styles.

    Args:
        paths (list[Path] | None): Files or directories to process. Defaults to
            'src/'.
        line_length (int | None): The maximum line length to wrap docstrings to.
        style (DocstringStyle | None): The docstring style to format to.
        exclude (list[str] | None): Glob patterns for paths to exclude.
        diff (bool): If True, print a unified diff to stdout instead of writing
            files.
    """
    resolved_paths, resolved_line_length, resolved_exclude, file_config = (
        _resolve_common_options(paths=paths, line_length=line_length, exclude=exclude)
    )
    resolved_style = style or DocstringStyle(
        file_config.get("style", DEFAULT_STYLE.value)
    )

    _validate_supported_style(resolved_style)

    validate_paths(paths=resolved_paths)
    python_files = collect_python_files(
        paths=resolved_paths,
        exclude_patterns=resolved_exclude,
    )

    _process_files(
        python_files=python_files,
        visitor_factory=lambda: DocstringVisitor(
            line_length=resolved_line_length,
            from_style=resolved_style,
            to_style=resolved_style,
        ),
        diff=diff,
    )


@app.command("convert")
def convert_command(
    from_style: Annotated[
        DocstringStyle,
        typer.Option("--from-style", help="Docstring style to convert from."),
    ],
    to_style: Annotated[
        DocstringStyle,
        typer.Option("--to-style", help="Docstring style to convert to."),
    ],
    paths: Annotated[list[Path] | None, _PATHS_ARGUMENT] = None,
    line_length: Annotated[int | None, _LINE_LENGTH_OPTION] = None,
    exclude: Annotated[list[str] | None, _EXCLUDE_OPTION] = None,
    diff: Annotated[bool, _DIFF_OPTION] = False,
) -> None:
    """Converts Python docstrings in the given files or directories from one
    style to another.

    Processes all .py files found at the provided paths, reparsing and re-
    rendering their docstrings from from_style to to_style in place. Directories
    are searched recursively. Unlike format_command, from_style and to_style
    have no config-file or default fallback -- both must be given explicitly on
    every invocation, since there is no sensible default for either side of a
    conversion.

    Args:
        from_style (DocstringStyle): The docstring style to convert from.
        to_style (DocstringStyle): The docstring style to convert to.
        paths (list[Path] | None): Files or directories to process. Defaults to
            'src/'.
        line_length (int | None): The maximum line length to wrap docstrings to.
        exclude (list[str] | None): Glob patterns for paths to exclude.
        diff (bool): If True, print a unified diff to stdout instead of writing
            files.

    Raises:
        typer.Exit: If from_style and to_style are the same.
    """
    if from_style == to_style:
        typer.echo(
            f"--from-style and --to-style were both '{from_style.value}'. "
            "Use the 'format' command instead when source and target styles "
            "match."
        )
        raise typer.Exit(code=1)

    _validate_supported_style(from_style)
    _validate_supported_style(to_style)

    resolved_paths, resolved_line_length, resolved_exclude, _ = _resolve_common_options(
        paths=paths, line_length=line_length, exclude=exclude
    )

    validate_paths(paths=resolved_paths)
    python_files = collect_python_files(
        paths=resolved_paths,
        exclude_patterns=resolved_exclude,
    )

    _process_files(
        python_files=python_files,
        visitor_factory=lambda: DocstringVisitor(
            line_length=resolved_line_length,
            from_style=from_style,
            to_style=to_style,
        ),
        diff=diff,
    )


if __name__ == "__main__":
    app()
