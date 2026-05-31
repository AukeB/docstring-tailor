"""Main module"""

from pathlib import Path
from typing import Annotated

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
from docstring_tailor.utils import collect_python_files, load_config, validate_paths

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
            DocstringVisitor(line_length=resolved_line_length)
        )
        file_path.write_text(modified_tree.code, encoding=ENCODING)


if __name__ == "__main__":
    app()


"""TODO:

- Currently, this code has been written specifically for the 'Google' docstring format. Fine for
now, but the end state goal is to have the functionality that the user can specify the style in the
pyproject.toml and that everything formats correctly to that style. The reading from pyproject.toml
is already there, the biggest effort is in reformatting docstring_section_formatter a bit to make it
work for all styles.

- Check all the parameters in the docstringformatter package to see which ones I also want.

- Implement feature that you can display the diff in terminal, instead of immediately formatting and
overwriting the .py files.

- Testing. Write more tests. Get to 100% code coverage. Redesign the structure of the 'tests/'
folder. All tests will be roughly the same, they have an input .py file from the 'raw' folder, which
will be formatted, and then it should be equal to the content of one of the files in the 'formatted'
folder. This means we can define a mapping that states which files in the raw folder should be
identical after formatting to a certain file in the formatted folder. In this way you may only need
one test function that just iterates over this mapping.
"""
