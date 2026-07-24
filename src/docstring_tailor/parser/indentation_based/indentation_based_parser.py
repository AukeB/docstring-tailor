"""Contains the abstract base parser for indentation-based docstring styles."""

from abc import abstractmethod
from inspect import cleandoc

from docstring_tailor.constants import (
    DOCSTRING_DELIMITER_LENGTH,
    DOCSTRING_KEYWORD_SEPARATOR,
)
from docstring_tailor.ir_model import (
    DocstringNode,
    NamedParagraph,
)
from docstring_tailor.parser.docstring_parser_base import DocstringParserBase
from docstring_tailor.parser.indentation_based.structured_list_parser import (
    StructuredListParserBase,
)


class IndentationBasedParser(DocstringParserBase):
    """Parses a raw docstring string into a typed intermediate representation
    using indentation- based section detection.

    The parsing pipeline operates in two phases:

    1. Indentation-based top-level scanning — identifies keyword-headed sections
       (NamedParagraph, StructuredList) by tracking indentation. Segment
       boundary rules differ enough between styles that this step is implemented
       per style (see _scan_top_level_segments).
    2. Flat content parsing — applies fence detection, blank-line splitting, and
       type classification to non-keyword content, and recursively to named
       paragraph bodies after dedenting. This step is identical across styles
       and fully shared.

    Subclasses supply the style-specific keyword sets, structured list parser
    instance, and top- level segment scanning rule; the classification pipeline
    beneath that is inherited unchanged.
    """

    def __init__(self) -> None:
        """Initialises the IndentationBasedParser."""
        self._structured_list_parser = self._create_structured_list_parser()

    @abstractmethod
    def _detect_structured_list_sections(self) -> frozenset[str]:
        """Returns the section keywords that map to structured list parsing for
        this docstring style.

        Returns:
            structured_list_sections (frozenset[str]): The set of keywords, e.g.
                'Args', 'Raises', 'Returns'.
        """
        ...

    @abstractmethod
    def _detect_named_paragraph_sections(self) -> frozenset[str]:
        """Returns the section keywords that map to named paragraph parsing for
        this docstring style.

        Returns:
            named_paragraph_sections (frozenset[str]): The set of keywords, e.g.
                'Note', 'Examples', 'See Also'.
        """
        ...

    @abstractmethod
    def _create_structured_list_parser(self) -> StructuredListParserBase:
        """Creates the structured list parser variant for this docstring style.

        Each style has fundamentally different item syntax within
        Args/Raises/Returns-like sections (e.g. NumPy's 'name : type' on its own
        line vs Google's 'name (type):' inline), so the concrete parser instance
        is supplied by the subclass rather than constructed here.

        Returns:
            structured_list_parser (StructuredListParserBase): The style-
                specific parser used to parse structured list section entries.
        """
        ...

    @abstractmethod
    def _scan_top_level_segments(
        self,
        lines: list[str],
        base_indent: int,
    ) -> list[tuple[bool, str]]:
        """Groups lines into keyword-section and plain-text segments using
        indentation only.

        The rule for where a keyword section ends differs enough between styles
        that this cannot be shared: Google's items sit deeper than their section
        header, so a line returning to base indentation reliably ends the
        section. NumPy's items sit at the *same* indentation as the header, so
        that same rule would truncate a NumPy section after its very first item.

        Args:
            lines (list[str]): All lines of the content to scan.
            base_indent (int): The indentation level of top-level content lines.

        Returns:
            segments (list[tuple[bool, str]]): Each entry is
                (is_keyword_section, content) where content is the raw joined
                lines for that segment.
        """
        ...

    def _parse_named_paragraph(self, content: str) -> NamedParagraph:
        """Parses a named paragraph section into a NamedParagraph node.

        Splits off the keyword header line and delegates the body to
        _parse_named_paragraph_body.

        Args:
            content (str): Raw section content including the keyword header
                line.

        Returns:
            named_paragraph (NamedParagraph): Fully parsed node with typed body.
        """
        lines = content.splitlines()
        header = lines[0].strip().rstrip(DOCSTRING_KEYWORD_SEPARATOR)
        body_content = "\n".join(lines[1:])
        body = self._parse_named_paragraph_body(body_content)

        named_paragraph = NamedParagraph(header=header, body=body)

        return named_paragraph

    def _parse_keyword_section(self, content: str) -> DocstringNode:
        """Dispatches a keyword-headed section to the appropriate parser.

        Args:
            content (str): Raw section content including the keyword header
                line.

        Returns:
            node (DocstringNode): A StructuredList or NamedParagraph node.
        """
        keyword = content.splitlines()[0].strip().rstrip(DOCSTRING_KEYWORD_SEPARATOR)

        if keyword in self._detect_structured_list_sections():
            node = self._structured_list_parser.parse(content)
        else:
            node = self._parse_named_paragraph(content)

        return node

    def _parse_top_level(self, content: str) -> list[DocstringNode]:
        """Parses top-level docstring content using indentation-based segment
        scanning.

        1. Determines base indentation from non-empty lines.
        2. Scans lines into keyword-section and plain-text segments.
        3. Dispatches each segment to the appropriate parser.

        Args:
            content (str): Raw docstring body with triple-quote delimiters
                stripped.

        Returns:
            nodes (list[DocstringNode]): Fully parsed IR.
        """
        lines = content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]

        if not non_empty_lines:
            return []

        base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        segments = self._scan_top_level_segments(lines, base_indent)

        nodes: list[DocstringNode] = []

        for is_keyword, segment_content in segments:
            if is_keyword:
                nodes.append(self._parse_keyword_section(segment_content))
            else:
                nodes.extend(self._parse_flat_content(segment_content))

        return nodes

    def parse(self, content: str) -> list[DocstringNode]:
        """Parses a raw docstring string into a typed IR.

        Strips triple-quote delimiters and delegates to _parse_top_level.

        Args:
            content (str): Raw docstring string including triple-quote
                delimiters.

        Returns:
            ir (list[DocstringNode]): Fully parsed and typed IR.
        """
        docstring_body = cleandoc(
            content[DOCSTRING_DELIMITER_LENGTH:-DOCSTRING_DELIMITER_LENGTH]
        )

        ir = self._parse_top_level(docstring_body)

        return ir
