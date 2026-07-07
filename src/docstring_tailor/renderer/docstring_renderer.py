"""Contains logic for rendering docstrings from a parsed IR."""

import re
import textwrap

from docstring_tailor.defaults.constants import (
    DOCSTRING_DELIMITER,
    DOCSTRING_DELIMITER_LENGTH,
)
from docstring_tailor.defaults.ir_model import (
    CodeBlock,
    CodeREPL,
    DocstringNode,
    NamedParagraph,
    Paragraph,
    SimpleList,
    StructuredList,
    StructuredListParameter,
)
from docstring_tailor.utils.utils_formatting import (
    format_code,
    format_text,
)


class DocstringRenderer:
    """Renders a parsed docstring IR into the Google docstring format.

    Receives a list of typed DocstringNode objects from the parser and renders
    each according to its concrete type. The final result is rendered as a one-
    line docstring when the IR is empty or consists of a single Paragraph node
    that fits within the line length limit, and as a multi-line docstring
    otherwise.

    Attributes:
        _line_length (int): Maximum characters per line including indentation.
        _current_indent (str): The accumulated indentation string at the current
            nesting level.
        _indent_unit (str): The indentation unit string used in the source file.
        _indent_length (int): Length of _indent_unit.
        _paragraph_separator (str): Separator inserted between rendered
            paragraphs.
        _line_separator (str): Separator inserted between rendered lines.
        _line_separator_indented (str): Line separator followed by one
            additional indentation level.
        _wrap_width (int): Maximum content width after accounting for current
            indentation.
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
            line_length (int): Maximum characters per line including
                indentation.
            current_indent (str): The accumulated indentation string at the
                current nesting level.
            indent_unit (str): The indentation unit string used in the source
                file.
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

    def _render_one_line(self, ir: list[DocstringNode]) -> str | None:
        """Renders the IR as a one-line docstring, if it qualifies.

        A docstring can only be rendered on one line when it is empty, or when
        it is a single Paragraph node with no other structure. Every other IR
        shape always renders to at least two physical lines once its own
        delimiters or markers are accounted for, so those cases are rejected
        immediately without attempting a render.

        1. Determines the raw content: empty string, or the sole Paragraph's
           text.
        2. Normalizes internal whitespace to single spaces.
        3. Rejects the one-line rendering if the delimited content exceeds the
           wrap width.

        Args:
            ir (list[DocstringNode]): Fully parsed and typed IR from
                DocstringParser.

        Returns:
            one_line (str | None): The rendered one-line docstring including
                triple-quote delimiters, or None if the IR does not qualify or
                is too long to fit.
        """
        if not ir:
            content = ""
        elif len(ir) == 1 and isinstance(ir[0], Paragraph):
            content = ir[0].content
        else:
            return None

        normalized = re.sub(r"\s+", " ", content.strip()) or " "
        total_length = (
            len(self._current_indent) + len(normalized) + 2 * DOCSTRING_DELIMITER_LENGTH
        )

        if total_length > self._wrap_width:
            return None

        one_line = DOCSTRING_DELIMITER + normalized + DOCSTRING_DELIMITER

        return one_line

    def _opens_with_block(self, ir: list[DocstringNode]) -> bool:
        """Determines whether the rendered docstring must start with a leading
        newline.

        A structural block -- CodeBlock, CodeREPL, SimpleList, StructuredList,
        or NamedParagraph -- cannot follow the opening triple quotes on the same
        line. The first node's type alone determines this, so no rendered text
        needs inspecting for fence markers, REPL prompts, list markers, or
        section keywords.

        Args:
            ir (list[DocstringNode]): Fully parsed and typed IR from
                DocstringParser.

        Returns:
            result (bool): True if a leading newline must be inserted before the
                first node.
        """
        result = bool(ir) and not isinstance(ir[0], Paragraph)

        return result

    def _render_opening_paragraph(self, paragraph: str) -> str:
        """Renders the first paragraph, accounting for the opening triple quotes
        offset.

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

    def _render_named_paragraph_chunk(self, node: DocstringNode) -> str:
        """Renders a single node from within a named paragraph body.

        Args:
            node (DocstringNode): A node from NamedParagraph.body. In practice
                always one of CodeBlock, CodeREPL, SimpleList, or Paragraph --
                StructuredList and NamedParagraph never appear here, since
                neither is permitted to nest inside a named paragraph's body.

        Returns:
            rendered (str): The rendered node string.

        Raises:
            ValueError: If the node is not a recognized DocstringNode subtype.
        """
        if isinstance(node, CodeBlock):
            rendered_content = format_code(
                text=node.code,
                line_separator=self._line_separator_indented,
            )
            indented = self._current_indent + self._indent_unit
            rendered = (
                node.delimiter
                + "\n"
                + indented
                + rendered_content
                + "\n"
                + indented
                + node.delimiter
            )
        elif isinstance(node, SimpleList):
            rendered = self._render_simple_list(
                node,
                wrap_width=self._wrap_width_indented,
                line_separator=self._line_separator_indented,
            )
        elif isinstance(node, CodeREPL):
            rendered = format_code(
                text=node.code,
                line_separator=self._line_separator_indented,
            )
        elif isinstance(node, Paragraph):
            rendered = format_text(
                text=node.content,
                wrap_width=self._wrap_width_indented,
                line_separator=self._line_separator_indented,
            )
        else:
            raise ValueError

        return rendered

    def _render_named_paragraph(self, section: NamedParagraph) -> str:
        """Renders a NAMED_PARAGRAPH section, rendering each body node
        independently.

        Args:
            section (NamedParagraph): A parsed named paragraph node.

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

    def _render_simple_list(
        self,
        section: SimpleList,
        *,
        wrap_width: int,
        line_separator: str,
    ) -> str:
        """Renders a SIMPLE_LIST section by rendering each parsed item
        independently.

        Each item is wrapped using format_text with a subsequent indent derived
        from the list marker width. For unordered lists this is always 2 spaces
        ('- '). For ordered lists it is derived from the total number of items,
        since longer lists produce wider markers (e.g. '10. ' vs '1. ').

        `wrap_width` and `line_separator` are required, with no default, so
        every call site must state explicitly which indentation level the list
        sits at. A SimpleList rendered at the top level uses
        `self._wrap_width`/`self._line_separator`; one nested inside a
        NamedParagraph body sits one level deeper and needs
        `self._wrap_width_indented`/`self._line_separator_indented`. A default
        here would risk silently reintroducing the bug this fixes: a nested
        list's first item is indented correctly by the NamedParagraph's own
        chunk separator, but every other item is joined using whatever
        `line_separator` this method falls back to -- so if that fallback were
        the shallower top-level one, only the first item would look right.

        Args:
            section (SimpleList): A parsed simple list node.
            wrap_width (int): Maximum content width for wrapping each item.
            line_separator (str): Separator inserted between wrapped lines and
                between items.

        Returns:
            rendered (str): The rendered list string.
        """
        if section.list_type == "unordered":
            marker_width = len("- ")
            formatted_items = [f"- {item}" for item in section.items]
        else:
            marker_width = len(str(len(section.items))) + len(". ")
            formatted_items = [
                f"{index + 1}. {item}" for index, item in enumerate(section.items)
            ]

        subsequent_indent = " " * marker_width

        rendered_items = [
            format_text(
                text=item,
                wrap_width=wrap_width,
                line_separator=line_separator,
                subsequent_indent=subsequent_indent,
            )
            for item in formatted_items
        ]

        rendered = line_separator.join(rendered_items)

        return rendered

    def _render_structured_list(self, section: StructuredList) -> str:
        """Renders a STRUCTURED_LIST section by rendering each entry and
        reassembling.

        Dispatches each entry to the appropriate item text format based on its
        type, then wraps the result in the section header.

        Args:
            section (StructuredList): A parsed structured list node.

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

    def _render_code_block(self, section: CodeBlock) -> str:
        """Renders a CODE_BLOCK section, wrapping content in its original fence
        delimiter.

        Args:
            section (CodeBlock): A parsed code block node.

        Returns:
            rendered (str): The re-indented code block string including fence
                delimiters.
        """
        rendered_content = format_code(
            text=section.code,
            line_separator=self._line_separator,
        )

        rendered = (
            section.delimiter
            + "\n"
            + self._current_indent
            + rendered_content
            + "\n"
            + self._current_indent
            + section.delimiter
        )

        return rendered

    def _render_node(self, node: DocstringNode) -> str:
        """Dispatches a single IR node to the appropriate renderer.

        Args:
            node (DocstringNode): Any IR node.

        Returns:
            rendered (str): The rendered node string.

        Raises:
            ValueError: If the node is not a recognized DocstringNode subtype.
        """
        if isinstance(node, CodeBlock):
            rendered = self._render_code_block(node)
        elif isinstance(node, StructuredList):
            rendered = self._render_structured_list(node)
        elif isinstance(node, SimpleList):
            rendered = self._render_simple_list(
                node,
                wrap_width=self._wrap_width,
                line_separator=self._line_separator,
            )
        elif isinstance(node, NamedParagraph):
            rendered = self._render_named_paragraph(node)
        elif isinstance(node, CodeREPL):
            rendered = format_code(
                text=node.code,
                line_separator=self._line_separator,
            )
        elif isinstance(node, Paragraph):
            rendered = format_text(
                text=node.content,
                wrap_width=self._wrap_width,
                line_separator=self._line_separator,
            )
        else:
            raise ValueError

        return rendered

    def _render_nodes(self, ir: list[DocstringNode]) -> list[str]:
        """Renders each IR node to its multi-line string form.

        The first node is given special treatment when it is a Paragraph, since
        the opening triple quotes consume space on the first physical line that
        the wrapping must account for -- a concern of document position, not of
        the Paragraph type itself, so it is handled here rather than inside
        _render_node.

        Args:
            ir (list[DocstringNode]): Fully parsed and typed IR from
                DocstringParser.

        Returns:
            rendered_parts (list[str]): Each node rendered to its string form,
                in order.
        """
        rendered_parts: list[str] = []

        for index, node in enumerate(ir):
            if index == 0 and isinstance(node, Paragraph):
                rendered_parts.append(self._render_opening_paragraph(node.content))
            else:
                rendered_parts.append(self._render_node(node))

        return rendered_parts

    def render(self, ir: list[DocstringNode]) -> str:
        """Renders a parsed docstring IR into a Google-style docstring string.

        Attempts a one-line rendering first, since that is only ever possible
        for an empty IR or a single Paragraph node short enough to fit within
        the wrap width. Every other IR shape renders each node independently,
        joins them with paragraph separators, and wraps the result in triple
        quotes as a multi-line docstring.

        Args:
            ir (list[DocstringNode]): Fully parsed and typed IR from
                DocstringParser.

        Returns:
            rendered_docstring (str): The fully rendered docstring string.
        """
        one_line = self._render_one_line(ir)

        if one_line is not None:
            return one_line

        rendered_parts = self._render_nodes(ir)
        rendered_content = self._paragraph_separator.join(rendered_parts)

        if self._opens_with_block(ir):
            rendered_content = "\n" + self._current_indent + rendered_content

        rendered_docstring = (
            DOCSTRING_DELIMITER
            + rendered_content
            + "\n"
            + self._current_indent
            + DOCSTRING_DELIMITER
        )

        return rendered_docstring
