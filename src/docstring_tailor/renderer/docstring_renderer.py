"""Contains logic for rendering docstrings from a parsed IR."""

import re
import textwrap

from docstring_tailor.defaults.constants import (
    DOCSTRING_DELIMITER,
    DOCSTRING_DELIMITER_LENGTH,
)
from docstring_tailor.defaults.ir_model import (
    DocstringNode,
    DocstringSection,
    ParsedNamedParagraph,
    ParsedSimpleList,
    ParsedStructuredList,
    SectionType,
    StructuredListParameter,
)
from docstring_tailor.utils.utils_formatting import (
    format_code,
    format_text,
)


class DocstringRenderer:
    """Renders a parsed docstring IR into the Google docstring format.

    Receives a list of typed DocstringNode objects from the parser and
    renders each according to its section type. The final result is
    rendered as a one-line docstring if it fits within the line length
    limit and contains no deliberate paragraph breaks, and as a
    multi-line docstring otherwise.

    Attributes:
        _line_length (int): Maximum characters per line including indentation.
        _current_indent (str): The accumulated indentation string at the current nesting level.
        _indent_unit (str): The indentation unit string used in the source file.
        _indent_length (int): Length of _indent_unit.
        _paragraph_separator (str): Separator inserted between rendered paragraphs.
        _line_separator (str): Separator inserted between rendered lines.
        _line_separator_indented (str): Line separator followed by one additional indentation level.
        _wrap_width (int): Maximum content width after accounting for current indentation.
        _wrap_width_indented (int): Maximum content width for indented content.
    """

    def __init__(
        self,
        line_length: int,
        current_indent: str,
        indent_unit: str,
    ) -> None:
        """Initialises the DocstringRenderer.

        Args:
            line_length (int): Maximum characters per line including indentation.
            current_indent (str): The accumulated indentation string at the current nesting level.
            indent_unit (str): The indentation unit string used in the source file.
        """
        self._line_length = line_length
        self._current_indent = current_indent
        self._indent_unit = indent_unit

        self._indent_length = len(self._indent_unit)

        self._paragraph_separator: str = "\n\n" + self._current_indent
        self._line_separator: str = "\n" + self._current_indent
        self._line_separator_indented: str = self._line_separator + self._indent_unit

        self._wrap_width: int = self._line_length - len(self._current_indent)
        self._wrap_width_indented: int = self._wrap_width - self._indent_length

    def _fits_on_one_line(self, rendered_content: str) -> bool:
        """Returns True if the rendered content can be output as a one-line docstring.

        Args:
            rendered_content (str): The fully rendered docstring content.

        Returns:
            result (bool): True if the content fits on one line, False otherwise.
        """
        is_deliberately_multiline = "\n" in rendered_content.strip()
        normalized = re.sub(r"\s+", " ", rendered_content.strip())
        total_length = (
            len(self._current_indent) + len(normalized) + 2 * DOCSTRING_DELIMITER_LENGTH
        )
        result = not is_deliberately_multiline and total_length <= self._wrap_width

        return result

    def _render_named_paragraph_chunk(
        self, node: DocstringSection | ParsedSimpleList
    ) -> str:
        """Renders a single node from within a named paragraph body.

        Args:
            node (DocstringSection): A node from ParsedNamedParagraph.body.

        Returns:
            rendered (str): The rendered node string.
        """
        if isinstance(node, ParsedSimpleList):
            rendered = self._render_simple_list(node)
        elif isinstance(node, DocstringSection) and node.section_type in [
            SectionType.CODE_BLOCK,
            SectionType.CODE_REPL,
        ]:
            rendered = format_code(
                text=node.content,
                line_separator=self._line_separator_indented,
            )
        else:
            rendered = format_text(
                text=node.content,
                wrap_width=self._wrap_width_indented,
                line_separator=self._line_separator_indented,
            )

        return rendered

    def _render_named_paragraph(self, section: ParsedNamedParagraph) -> str:
        """Renders a NAMED_PARAGRAPH section, rendering each body node independently.

        Args:
            section (ParsedNamedParagraph): A parsed named paragraph node.

        Returns:
            rendered (str): The rendered named paragraph string.
        """
        chunk_separator = self._paragraph_separator + self._indent_unit

        rendered_body_nodes = [
            self._render_named_paragraph_chunk(node) for node in section.body
        ]

        body = chunk_separator.join(rendered_body_nodes)

        rendered = (
            section.header + ":\n" + self._current_indent + self._indent_unit + body
        )

        return rendered

    def _render_simple_list(self, section: ParsedSimpleList) -> str:
        """Renders a SIMPLE_LIST section by rendering each parsed item independently.

        Each item is wrapped using format_text with a subsequent indent derived
        from the list marker width. For unordered lists this is always 2 spaces
        ('- '). For ordered lists it is derived from the total number of items,
        since longer lists produce wider markers (e.g. '10. ' vs '1. ').

        Args:
            section (ParsedSimpleList): A parsed simple list node.

        Returns:
            rendered (str): The rendered list string.
        """
        if section.list_type == "unordered":
            subsequent_indent = " " * 2
            markers = [f"- {item}" for item in section.items]
        else:
            marker_width = len(str(len(section.items))) + 2
            subsequent_indent = " " * marker_width
            markers = [
                f"{index + 1}. {item}" for index, item in enumerate(section.items)
            ]

        rendered_items = [
            format_text(
                text=item,
                wrap_width=self._wrap_width,
                line_separator=self._line_separator,
                subsequent_indent=subsequent_indent,
            )
            for item in markers
        ]

        rendered = self._line_separator.join(rendered_items)

        return rendered

    def _render_structured_list(self, section: ParsedStructuredList) -> str:
        """Renders a STRUCTURED_LIST section by rendering each entry and reassembling.

        Dispatches each entry to the appropriate item text format based on its
        type, then wraps the result in the section header.

        Args:
            section (ParsedStructuredList): A parsed structured list node.

        Returns:
            rendered (str): The rendered structured list string.
        """
        rendered_entries: list[str] = []

        for entry in section.entries:
            item_text = (
                f"{entry.name} ({entry.type}): {entry.description}"
                if isinstance(entry, StructuredListParameter)
                else f"{entry.error_type}: {entry.description}"
            )

            rendered_entry = format_text(
                text=item_text,
                wrap_width=self._wrap_width_indented,
                line_separator=self._line_separator_indented,
                subsequent_indent=self._indent_unit,
            )

            rendered_entries.append(rendered_entry)

        body = self._line_separator_indented.join(rendered_entries)

        rendered = (
            section.keyword + ":\n" + self._current_indent + self._indent_unit + body
        )

        return rendered

    def _render_opening_paragraph(self, paragraph: str) -> str:
        """Renders the first paragraph, accounting for the opening triple quotes offset.

        Args:
            paragraph (str): The first plain text paragraph.

        Returns:
            rendered_paragraph (str): The wrapped paragraph string.
        """
        normalized = re.sub(r"\s+", " ", paragraph.strip())
        lines = textwrap.wrap(
            normalized,
            width=self._wrap_width,
            initial_indent=" " * DOCSTRING_DELIMITER_LENGTH,
            subsequent_indent="",
        )

        if lines:
            lines[0] = lines[0][DOCSTRING_DELIMITER_LENGTH:]

        rendered_paragraph = self._line_separator.join(lines)

        return rendered_paragraph

    def _render_node(self, node: DocstringNode, is_first: bool = False) -> str:
        """Dispatches a single IR node to the appropriate renderer.

        Args:
            node (DocstringSection): Any IR node.
            is_first (bool): Whether this is the first node in the IR, used
                to apply the opening paragraph offset.

        Returns:
            rendered (str): The rendered node string.
        """
        if isinstance(node, DocstringSection):
            if node.section_type is SectionType.PARAGRAPH:
                if is_first:
                    rendered = self._render_opening_paragraph(paragraph=node.content)
                else:
                    rendered = format_text(
                        text=node.content,
                        wrap_width=self._wrap_width,
                        line_separator=self._line_separator,
                    )
            elif node.section_type in [SectionType.CODE_BLOCK, SectionType.CODE_REPL]:
                rendered = format_code(
                    text=node.content,
                    line_separator=self._line_separator,
                )
        elif isinstance(node, ParsedStructuredList):
            rendered = self._render_structured_list(node)
        elif isinstance(node, ParsedSimpleList):
            rendered = self._render_simple_list(node)
        elif isinstance(node, ParsedNamedParagraph):
            rendered = self._render_named_paragraph(node)
        else:
            raise ValueError

        return rendered

    def render(self, ir: list[DocstringNode]) -> str:
        """Renders a parsed docstring IR into a Google-style docstring string.

        Renders each IR node independently, joins them with paragraph separators,
        then wraps the result in triple quotes as either a one-line or multi-line
        docstring.

        Args:
            ir (list[DocstringNode]): Fully parsed and typed IR from DocstringParser.

        Returns:
            rendered_docstring (str): The fully rendered docstring string.
        """
        rendered_parts: list[str] = []

        for index, node in enumerate(ir):
            is_first = index == 0
            rendered_parts.append(self._render_node(node=node, is_first=is_first))

        rendered_content = self._paragraph_separator.join(rendered_parts)

        first_line = next(
            (l.strip() for l in rendered_content.split("\n") if l.strip()), ""
        )
        opens_with_block = (
            first_line.startswith(("```", "~~~"))
            or re.match(r"^[-*+]\s+|^\d+[.)]\s+", first_line) is not None
        )

        if opens_with_block:
            rendered_content = "\n" + self._current_indent + rendered_content

        if self._fits_on_one_line(rendered_content):
            normalized = re.sub(r"\s+", " ", rendered_content.strip())
            rendered_docstring = DOCSTRING_DELIMITER + normalized + DOCSTRING_DELIMITER
        else:
            rendered_docstring = (
                DOCSTRING_DELIMITER
                + rendered_content
                + "\n"
                + self._current_indent
                + DOCSTRING_DELIMITER
            )

        return rendered_docstring
