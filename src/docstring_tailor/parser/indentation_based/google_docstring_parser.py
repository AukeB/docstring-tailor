"""Contains the Google-style docstring parser."""

from docstring_tailor.constants import (
    DOCSTRING_KEYWORD_SEPARATOR,
    GOOGLE_NAMED_PARAGRAPH_SECTIONS,
    GOOGLE_STRUCTURED_LIST_SECTIONS,
)
from docstring_tailor.parser.indentation_based.indentation_based_parser import (
    IndentationBasedParser,
)
from docstring_tailor.parser.indentation_based.structured_list_parser import (
    GoogleStructuredListParser,
    StructuredListParserBase,
)


class GoogleDocstringParser(IndentationBasedParser):
    """Parses Google-style docstrings into a typed intermediate representation.

    Implements the style-specific hooks required by IndentationBasedParser: the
    structured list parser instance, the keyword sets that distinguish
    structured list sections (Args, Raises, Returns) from named paragraph
    sections (Note, Examples, See Also), and top-level segment scanning. The
    flat-content classification pipeline beneath that is fully inherited.
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

    def _create_structured_list_parser(self) -> StructuredListParserBase:
        """Creates the structured list parser for Google-style docstrings.

        Returns:
            structured_list_parser (StructuredListParserBase): Parser for
                Args/Raises/Returns- like sections written in Google style.
        """
        structured_list_parser = GoogleStructuredListParser()

        return structured_list_parser

    def _scan_top_level_segments(
        self,
        lines: list[str],
        base_indent: int,
    ) -> list[tuple[bool, str]]:
        """Groups lines into keyword-section and plain-text segments using
        indentation only.

        A keyword line at base indentation starts a new keyword segment. All
        subsequent lines more indented than base belong to that segment's body,
        regardless of any blank lines within. A non-keyword line returning to
        base indentation ends the keyword segment and starts a new plain
        segment. This relies on Google's items always sitting deeper than their
        section header.

        Args:
            lines (list[str]): All lines of the content to scan.
            base_indent (int): The indentation level of top-level content lines.

        Returns:
            segments (list[tuple[bool, str]]): Each entry is
                (is_keyword_section, content) where content is the raw joined
                lines for that segment.
        """
        segments: list[tuple[bool, str]] = []
        current_lines: list[str] = []
        current_is_keyword = False
        blank_buffer: list[str] = []

        for line in lines:
            if not line.strip():
                blank_buffer.append(line)
                continue

            indent = len(line) - len(line.lstrip())
            keyword = line.strip().rstrip(DOCSTRING_KEYWORD_SEPARATOR)
            is_base = indent == base_indent
            is_keyword_line = is_base and (
                keyword in self._detect_named_paragraph_sections()
                or keyword in self._detect_structured_list_sections()
            )

            if is_keyword_line:
                if current_lines:
                    segments.append((current_is_keyword, "\n".join(current_lines)))
                current_lines = [line]
                current_is_keyword = True
                blank_buffer = []
            elif is_base and current_is_keyword:
                segments.append((True, "\n".join(current_lines)))
                current_lines = [line]
                current_is_keyword = False
                blank_buffer = []
            else:
                current_lines.extend(blank_buffer)
                blank_buffer = []
                current_lines.append(line)

        if current_lines:
            segments.append((current_is_keyword, "\n".join(current_lines)))

        return segments
