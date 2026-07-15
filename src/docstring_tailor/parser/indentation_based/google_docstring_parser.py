"""Contains the Google-style docstring parser."""

from docstring_tailor.constants import (
    GOOGLE_NAMED_PARAGRAPH_SECTIONS,
    GOOGLE_STRUCTURED_LIST_SECTIONS,
)
from docstring_tailor.parser.indentation_based.google_structured_list_parser import (
    GoogleStructuredListParser,
)
from docstring_tailor.parser.indentation_based.indentation_based_parser import (
    IndentationBasedParser,
)


class GoogleDocstringParser(IndentationBasedParser):
    """Parses Google-style docstrings into a typed intermediate representation.

    Implements the style-specific hooks required by IndentationBasedParser: the
    structured list parser instance, and the keyword sets that distinguish
    structured list sections (Args, Raises, Returns) from named paragraph
    sections (Note, Examples, See Also). The scanning and classification
    pipeline itself is fully inherited.
    """

    def _detect_structured_list_sections(self) -> frozenset[str]:
        """Returns the Google-style structured list section keywords.

        Returns:
            structured_list_sections (frozenset[str]): Keywords such as 'Args',
                'Raises', 'Returns', 'Yields', 'Attributes'.
        """
        structured_list_sections = GOOGLE_STRUCTURED_LIST_SECTIONS

        return structured_list_sections

    def _detect_named_paragraph_sections(self) -> frozenset[str]:
        """Returns the Google-style named paragraph section keywords.

        Returns:
            named_paragraph_sections (frozenset[str]): Keywords such as 'Note',
                'Examples', 'See Also', 'Warning'.
        """
        named_paragraph_sections = GOOGLE_NAMED_PARAGRAPH_SECTIONS

        return named_paragraph_sections

    def _create_structured_list_parser(self) -> GoogleStructuredListParser:
        """Creates the structured list parser for Google-style docstrings.

        Returns:
            structured_list_parser (StructuredListParser): Parser for
                Args/Raises/Returns-like sections written in Google style.
        """
        structured_list_parser = GoogleStructuredListParser()

        return structured_list_parser
