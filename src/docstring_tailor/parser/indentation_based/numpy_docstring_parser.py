"""Contains the NumPy-style docstring parser."""

from docstring_tailor.constants import (
    NUMPY_ITEM_SECTIONS,
    NUMPY_PLAIN_SECTIONS,
    RE_PATTERN_NUMPY_SECTION_UNDERLINE,
)
from docstring_tailor.parser.indentation_based.indentation_based_parser import (
    IndentationBasedParser,
)
from docstring_tailor.parser.indentation_based.structured_list_parser import (
    NumpyStructuredListParser,
    StructuredListParserBase,
)


class NumpyDocstringParser(IndentationBasedParser):
    """Parses NumPy-style docstrings into a typed intermediate representation.

    Implements the style-specific hooks required by IndentationBasedParser: the
    structured list parser instance, the keyword sets that distinguish
    structured list sections (Parameters, Raises, Returns) from named paragraph
    sections (Notes, Examples, See Also), and top-level segment scanning. The
    flat-content classification pipeline beneath that is fully inherited.
    """

    def _detect_structured_list_sections(self) -> frozenset[str]:
        """Returns the NumPy-style structured list section keywords.

        Returns:
            structured_list_sections (frozenset[str]): Keywords such as
                'Parameters', 'Raises', 'Returns', 'Yields', 'Attributes'.
        """
        structured_list_sections = NUMPY_ITEM_SECTIONS

        return structured_list_sections

    def _detect_named_paragraph_sections(self) -> frozenset[str]:
        """Returns the NumPy-style named paragraph section keywords.

        Returns:
            named_paragraph_sections (frozenset[str]): Keywords such as 'Notes',
                'Examples', 'See Also', 'References'.
        """
        named_paragraph_sections = NUMPY_PLAIN_SECTIONS

        return named_paragraph_sections

    def _create_structured_list_parser(self) -> StructuredListParserBase:
        """Creates the structured list parser for NumPy-style docstrings.

        Returns:
            structured_list_parser (StructuredListParserBase): Parser for
                Parameters/Raises/Returns- like sections written in NumPy style.
        """
        structured_list_parser = NumpyStructuredListParser()

        return structured_list_parser

    def _is_section_header(self, lines: list[str], index: int) -> bool:
        """Checks whether the line at the given index is a NumPy section header.

        A NumPy section header is a recognised keyword sitting alone on its
        line, immediately followed by a dashed underline. Requiring the
        underline (rather than a keyword match alone) avoids misclassifying
        prose that happens to start with a matching word, e.g. a sentence
        beginning 'Notes on this method apply only when...'.

        Args:
            lines (list[str]): All lines being scanned. index (int): The index
                of the candidate header line.

        Returns:
            result (bool): True if the line at index is a genuine section
                header.
        """
        keyword = lines[index].strip()
        is_recognised_keyword = (
            keyword in self._detect_named_paragraph_sections()
            or keyword in self._detect_structured_list_sections()
        )

        if not is_recognised_keyword:
            return False

        next_index = index + 1

        if next_index >= len(lines):
            return False

        result = bool(
            RE_PATTERN_NUMPY_SECTION_UNDERLINE.match(lines[next_index].strip())
        )

        return result

    def _scan_top_level_segments(
        self,
        lines: list[str],
        base_indent: int,
    ) -> list[tuple[bool, str]]:
        """Groups lines into keyword-section and plain-text segments using
        indentation and the dashed-underline section marker.

        Unlike Google, NumPy's items sit at the *same* indentation as their
        section header rather than deeper, so a section cannot be ended simply
        by returning to base indentation -- that would truncate it after its
        first item. Instead, a section only ends when the next confirmed section
        header (keyword line plus underline) is found, or the content runs out.
        The underline itself is consumed as a delimiter and dropped from the
        segment content; everything else from the original lines is preserved
        untouched.

        Args:
            lines (list[str]): All lines of the content to scan.
            base_indent (int): The indentation level of top-level content lines.

        Returns:
            segments (list[tuple[bool, str]]): Each entry is
                (is_keyword_section, content) where content is the raw joined
                lines for that segment, with any consumed underline lines
                excluded.
        """
        segments: list[tuple[bool, str]] = []
        current_lines: list[str] = []
        current_is_keyword = False
        blank_buffer: list[str] = []
        index = 0

        while index < len(lines):
            line = lines[index]

            if not line.strip():
                blank_buffer.append(line)
                index += 1
                continue

            indent = len(line) - len(line.lstrip())
            is_base = indent == base_indent
            is_section_header = is_base and self._is_section_header(lines, index)

            if is_section_header:
                if current_lines:
                    segments.append((current_is_keyword, "\n".join(current_lines)))
                current_lines = [line]
                current_is_keyword = True
                blank_buffer = []
                # Skip the underline line -- it is a delimiter marking the
                # section boundary, not content, and carries no information
                # once the boundary has been recognised.
                index += 2
                continue

            current_lines.extend(blank_buffer)
            blank_buffer = []
            current_lines.append(line)
            index += 1

        if current_lines:
            segments.append((current_is_keyword, "\n".join(current_lines)))

        return segments
