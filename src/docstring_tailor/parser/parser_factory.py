"""Factory for instantiating the correct docstring parser for a given style."""

from docstring_tailor.cli_config import DocstringStyle
from docstring_tailor.parser.indentation_based.google_docstring_parser import (
    GoogleDocstringParser,
)
from docstring_tailor.parser.indentation_based.indentation_based_parser import (
    IndentationBasedParser,
)
from docstring_tailor.parser.indentation_based.numpy_docstring_parser import (
    NumpyDocstringParser,
)

# Maps each supported style to its parser class. Sphinx and Epydoc will add
# entries here once their (directive-based) parsers exist.
_PARSER_CLASSES: dict[str, type[IndentationBasedParser]] = {
    DocstringStyle.google: GoogleDocstringParser,
    DocstringStyle.numpy: NumpyDocstringParser,
}


def create_parser(style: DocstringStyle) -> IndentationBasedParser:
    """Instantiates the parser for the given docstring style.

    Args:
        style (DocstringStyle): The docstring style to parse.

    Returns:
        parser (IndentationBasedParser): A fresh parser instance for style.

    Raises:
        ValueError: If style has no registered parser.
    """
    parser_class = _PARSER_CLASSES.get(style)

    if parser_class is None:
        raise ValueError(f"No parser registered for style {style.value!r}.")

    parser = parser_class()

    return parser
