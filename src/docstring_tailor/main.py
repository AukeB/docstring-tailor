"""Main module"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Optional

import libcst as cst
import typer

from docstring_tailor.cli_config import (
    DEFAULT_PATHS,
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


def _pluralize_files(file_count: int) -> str:
    """Returns the correctly pluralized noun for a file count.

    Args:
        file_count (int): The number of files.

    Returns:
        noun (str): 'file' when count is 1, 'files' otherwise.
    """
    noun = "file" if file_count == 1 else "files"

    return noun


def _format_run_summary(counter_reformatted: int, counter_unchanged: int) -> str:
    """Builds a Ruff-style one-line summary of a formatting run.

    Mirrors 'ruff format': only the non-zero categories are named, except when
    nothing was processed at all, in which case both are reported as zero.

    Args:
        counter_reformatted (int): Number of files whose content changed.
        counter_unchanged (int): Number of files left unchanged.

    Returns:
        summary (str): The human-readable summary line.
    """
    reformatted_part = f"{counter_reformatted} {_pluralize_files(file_count=counter_reformatted)} reformatted"
    unchanged_part = f"{counter_unchanged} {_pluralize_files(file_count=counter_unchanged)} left unchanged"

    if counter_reformatted and counter_unchanged:
        format_summary = f"{reformatted_part}, {unchanged_part}"
    elif counter_reformatted:
        format_summary = reformatted_part
    elif counter_unchanged:
        format_summary = unchanged_part
    else:
        format_summary = "0 files reformatted, 0 files left unchanged"

    return format_summary


@dataclass(frozen=True)
class _FormatResult:
    """Outcome counts of a formatting run for multiple python files.

    Attributes:
        count_reformatted (int): Number of files whose content changed.
        count_unchanged (int): Number of files left untouched.
        count_errored (int): Number of files that could not be read, decoded, or
            parsed and were skipped.
    """

    count_reformatted: int
    count_unchanged: int
    count_errored: int


def _process_single_file(
    file_path: Path,
    visitor_factory: Callable[[], DocstringVisitor],
    diff: bool,
) -> bool:
    """Reads, transforms, and writes or diffs a single Python file.

    Args:
        file_path (Path): The file to process.
        visitor_factory (Callable[[], DocstringVisitor]): Builds a fresh
            DocstringVisitor this file.
        diff (bool): If True, print a diff instead of writing files.

    Returns:
        is_changed (bool): True if formatting changed the file's content.
    """
    input_data = file_path.read_text(encoding=ENCODING)
    input_tree = cst.parse_module(source=input_data)
    modified_tree = input_tree.visit(visitor_factory())

    modified_code = modified_tree.code
    is_changed = modified_code != input_data

    if diff:
        show_diff(original=input_data, modified=modified_code, path=file_path)
    elif is_changed:
        file_path.write_text(modified_code, encoding=ENCODING)

    return is_changed


def _process_files(
    python_files: list[Path],
    visitor_factory: Callable[[], DocstringVisitor],
    diff: bool,
) -> _FormatResult:
    """Parses, transforms, and writes or diffs each collected Python file.

    A fresh DocstringVisitor is created per file via visitor_factory, since
    DocstringVisitor accumulates indentation state as it traverses a single
    file's CST and cannot be safely reused across files. Unchanged files are not
    rewritten, so their on-disk timestamps are preserved. In write mode a Ruff-
    style summary of the run is printed once all files are processed.

    A file that cannot be read, decoded, or parsed as Python is reported to
    stderr and skipped, so a single malformed file never aborts the whole run
    and every other file is still processed.

    Args:
        python_files (list[Path]): The collected files to process.
        visitor_factory (Callable[[], DocstringVisitor]): Builds a fresh
            DocstringVisitor for each file.
        diff (bool): If True, print a diff instead of writing files.

    Returns:
        result (_FormatResult): Counts of reformatted, unchanged, and errored
            files, so the caller can choose an exit code.

    Raises:
        OSError: If the file cannot be read or written.
        UnicodeDecodeError: If the file is not valid text in the expected
            encoding.
        cst.ParserSyntaxError: If the file is not valid python.
    """
    counter_reformatted: int = 0
    counter_unchanged: int = 0
    counter_errored: int = 0

    for file_path in python_files:
        try:
            is_changed: bool = _process_single_file(
                file_path=file_path,
                visitor_factory=visitor_factory,
                diff=diff,
            )
        except OSError as error:
            typer.echo(
                f"error: could not read or write '{file_path}': {error}", err=True
            )
            counter_errored += 1
            continue
        except UnicodeDecodeError as error:
            typer.echo(
                f"error: '{file_path}' is not valid {ENCODING} text: {error}", err=True
            )
            counter_errored += 1
            continue
        except cst.ParserSyntaxError as error:
            typer.echo(f"error: '{file_path}' is not valid Python: {error}", err=True)
            counter_errored += 1
            continue

        if is_changed:
            counter_reformatted += 1
        else:
            counter_unchanged += 1

    if not diff:
        typer.echo(
            _format_run_summary(
                counter_reformatted=counter_reformatted,
                counter_unchanged=counter_unchanged,
            )
        )

    return _FormatResult(
        count_reformatted=counter_reformatted,
        count_unchanged=counter_unchanged,
        count_errored=counter_errored,
    )


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

    Raises:
        typer.Exit: With code 1 if any file could not be processed, or, in
            --diff mode, if any file would be reformatted, so --diff can gate a
            CI run while a normal write run still succeeds after fixing files.
    """
    resolved_paths, resolved_line_length, resolved_exclude, file_config = (
        _resolve_common_options(paths=paths, line_length=line_length, exclude=exclude)
    )

    resolved_style = style or file_config.get("style")

    if resolved_style is None:
        typer.echo(
            "Error: Docstring style not specified. "
            "Pass --style on the command line or set 'style' in your config file "
            "(pyproject.toml or docstring_tailor.toml)."
        )
        raise typer.Exit(code=1)

    resolved_style = DocstringStyle(resolved_style)

    _validate_supported_style(resolved_style)

    validate_paths(paths=resolved_paths)
    python_files = collect_python_files(
        paths=resolved_paths,
        exclude_patterns=resolved_exclude,
    )

    format_result = _process_files(
        python_files=python_files,
        visitor_factory=lambda: DocstringVisitor(
            line_length=resolved_line_length,
            from_style=resolved_style,
            to_style=resolved_style,
        ),
        diff=diff,
    )

    # Write mode treats a reformat as success (files are fixed). Only --diff
    # gates on changes.
    if format_result.count_errored or (diff and format_result.count_reformatted):
        raise typer.Exit(code=1)


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
        typer.Exit: With code 1 if from_style and to_style are the same.
        typer.Exit: With code 1 if any file could not be processed.
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

    format_result = _process_files(
        python_files=python_files,
        visitor_factory=lambda: DocstringVisitor(
            line_length=resolved_line_length,
            from_style=from_style,
            to_style=to_style,
        ),
        diff=diff,
    )

    if format_result.count_errored:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
