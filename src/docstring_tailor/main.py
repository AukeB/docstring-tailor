"""Main module"""

from pathlib import Path
from typing import Annotated

import libcst as cst
import typer

from docstring_tailor.cli_config import (
    DEFAULT_PATHS,
    DEFAULT_STYLE,
    DETECT_LISTS_DEFAULT,
    LINE_LENGTH_DEFAULT,
    LINE_LENGTH_MAX,
    LINE_LENGTH_MIN,
    SUPPORTED_STYLES,
    DocstringStyle,
)
from docstring_tailor.constants import ENCODING
from docstring_tailor.docstring_visitor import DocstringVisitor
from docstring_tailor.utils.utils_file_system import (
    collect_python_files,
    load_config,
    validate_paths,
)

app = typer.Typer()


@app.command()
def main(
    paths: Annotated[
        list[Path] | None,
        typer.Argument(help="Files or directories to process. Defaults to 'src/'."),
    ] = None,
    style: Annotated[
        DocstringStyle | None,
        typer.Option("--style", help="Docstring style to format to."),
    ] = None,
    line_length: Annotated[
        int | None,
        typer.Option(
            "--line-length",
            help=f"Maximum line length. Must be between {LINE_LENGTH_MIN} and {LINE_LENGTH_MAX}.",
            min=LINE_LENGTH_MIN,
            max=LINE_LENGTH_MAX,
        ),
    ] = None,
    detect_lists: Annotated[
        bool | None,
        typer.Option(
            "--detect-lists/--no-detect-lists",
            help="Detect and preserve list formatting.",
        ),
    ] = None,
) -> None:
    """Formats Python docstrings in the given files or directories to the specified style.

    Processes all .py files found at the provided paths, reformatting their docstrings in place.
    Directories are searched recursively.

    Args:
        paths (list[Path] | None): Files or directories to process. Defaults to 'src/'.
        style (DocstringStyle | None): The docstring style to format to.
        line_length (int | None): The maximum line length to wrap docstrings to.
    """
    # Resolve configuration with priority: CLI argument > config file > built-in default.
    file_config = load_config()
    resolved_paths = paths or [Path(p) for p in DEFAULT_PATHS]
    resolved_style = style or DocstringStyle(
        file_config.get("style", DEFAULT_STYLE.value)
    )
    resolved_line_length = line_length or file_config.get(
        "line-length", LINE_LENGTH_DEFAULT
    )
    resolved_detect_lists = (
        detect_lists
        if detect_lists is not None
        else file_config.get("detect-lists", DETECT_LISTS_DEFAULT)
    )

    if resolved_style not in SUPPORTED_STYLES:
        typer.echo(
            f"Style '{resolved_style.value}' is not yet supported. "
            f"Currently supported: {', '.join(s.value for s in SUPPORTED_STYLES)}."
        )
        raise typer.Exit(code=1)

    validate_paths(paths=resolved_paths)
    python_files = collect_python_files(paths=resolved_paths)

    for file_path in python_files:
        input_data = file_path.read_text(encoding=ENCODING)
        input_tree = cst.parse_module(source=input_data)
        modified_tree = input_tree.visit(
            DocstringVisitor(
                line_length=resolved_line_length, detect_lists=resolved_detect_lists
            )
        )
        file_path.write_text(modified_tree.code, encoding=ENCODING)


if __name__ == "__main__":
    app()
