"""Main module"""

from pathlib import Path
from typing import Annotated

import libcst as cst
import typer

from src.docstring_tailor.cli_config import (
    DEFAULT_PATHS,
    DEFAULT_STYLE,
    LINE_LENGTH_DEFAULT,
    LINE_LENGTH_MAX,
    LINE_LENGTH_MIN,
    SUPPORTED_STYLES,
    DocstringStyle,
)

from src.docstring_tailor.constants import ENCODING
from src.docstring_tailor.utils import collect_python_files, validate_paths
from src.docstring_tailor.docstring_visitor import DocstringVisitor

app = typer.Typer()

@app.command()
def main(
    paths: Annotated[
        list[Path] | None,
        typer.Argument(help="Files or directories to process. Defaults to 'src/'."),
    ] = None,
    style: Annotated[
        DocstringStyle,
        typer.Option("--style", help="Docstring style to format to."),
    ] = DEFAULT_STYLE,
    line_length: Annotated[
        int,
        typer.Option(
            "--line-length",
            help=f"Maximum line length. Must be between {LINE_LENGTH_MIN} and {LINE_LENGTH_MAX}.",
            min=LINE_LENGTH_MIN,
            max=LINE_LENGTH_MAX,
        ),
    ] = LINE_LENGTH_DEFAULT,
) -> None:
    """
    Formats Python docstrings in the given files or directories to the specified style.

    Processes all .py files found at the provided paths, reformatting their docstrings
    in place. Directories are searched recursively.

    Args:
        paths (list[Path] | None): Files or directories to process. Defaults to 'src/'.
        style (DocstringStyle): The docstring style to format to.
        line_length (int): The maximum line length to wrap docstrings to.
    """
    if paths is None:
        paths = [Path(p) for p in DEFAULT_PATHS]

    if style not in SUPPORTED_STYLES:
        typer.echo(
            f"Style '{style.value}' is not yet supported. "
            f"Currently supported: {', '.join(f'{s.value}' for s in SUPPORTED_STYLES)}."
        )
        raise typer.Exit(code=1)

    validate_paths(paths=paths)

    python_files = collect_python_files(paths=paths)

    for file_path in python_files:
        input_data = file_path.read_text(encoding=ENCODING)
        input_tree = cst.parse_module(source=input_data)
        modified_tree = input_tree.visit(DocstringVisitor(line_length=line_length))
        file_path.write_text(modified_tree.code, encoding=ENCODING)


if __name__ == "__main__":
    app()