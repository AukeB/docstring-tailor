"""Factory for instantiating the correct docstring parser for a given style."""

from docstring_tailor.cli_config import DocstringStyle
from docstring_tailor.parser.directive_based.sphinx_docstring_parser import (
    SphinxDocstringParser,
)
from docstring_tailor.parser.docstring_parser_base import DocstringParserBase
from docstring_tailor.parser.indentation_based.google_docstring_parser import (
    GoogleDocstringParser,
)
from docstring_tailor.parser.indentation_based.numpy_docstring_parser import (
    NumpyDocstringParser,
)

# Maps each supported style to its parser class. Epydoc will add an entry here
# once its (directive-based) parsers exist.
_PARSER_CLASSES: dict[str, type[DocstringParserBase]] = {
    DocstringStyle.google: GoogleDocstringParser,
    DocstringStyle.numpy: NumpyDocstringParser,
    DocstringStyle.sphinx: SphinxDocstringParser,
}


def create_parser(style: DocstringStyle) -> DocstringParserBase:
    """Instantiates the parser for the given docstring style.

    Args:
        style (DocstringStyle): The docstring style to parse.

    Returns:
        parser (DocstringParserBase): A fresh parser instance for style.

    Raises:
        ValueError: If style has no registered parser.
    """
    parser_class = _PARSER_CLASSES.get(style)

    if parser_class is None:
        raise ValueError(f"No parser registered for style {style.value!r}.")

    parser = parser_class()

    return parser
