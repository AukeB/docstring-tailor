"""Contains the abstract base renderer shared by all docstring styles."""

import re
import textwrap
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext

from docstring_tailor.constants import (
    DOCSTRING_DELIMITER,
    DOCSTRING_DELIMITER_LENGTH,
    ORDERED_LIST_SEPARATOR,
    RE_PATTERN_WHITESPACE,
    UNORDERED_LIST_MARKER,
)
from docstring_tailor.ir_model import (
    CodeBlock,
    CodeREPL,
    DocstringNode,
    NamedParagraph,
    Paragraph,
    SimpleList,
    StructuredList,
    StructuredListError,
    StructuredListParameter,
)
from docstring_tailor.utils.utils_formatting import format_code, format_text


class DocstringRendererBase(ABC):
    """Renders a parsed docstring IR into a style-specific docstring string.

    Receives a list of typed DocstringNode objects from the parser and renders
    each according to its concrete type. The final result is rendered as a one-
    line docstring when the IR is empty or consists of a single Paragraph node
    that fits within the line length limit, and as a multi-line docstring
    otherwise.

    Two pieces are style-specific and left abstract: how a section header line
    is rendered (_render_section_header), and how a single structured list entry
    is rendered (_render_structured_list_entry) -- NumPy's header-line- plus-
    indented-description shape isn't a different string template like Google's
    inline format, it's a different physical-line structure, so this cannot be a
    shared string-formatting detail the way the header is. Everything else --
    node dispatch, joining, wrapping, indentation tracking -- is identical
    across styles and fully shared here.

    A structured list entry may be a StructuredListParameter OR a
    StructuredListError regardless of which parser produced the IR: when
    rendering an IR that was parsed in a different style and is being converted,
    a renderer must handle entry types its own parser never produces (e.g.
    NumPy's renderer must handle a StructuredListError coming from a Google-
    parsed Raises section).

    Mirrors the parser's own strategy for handling NamedParagraph content:
    rather than a second dispatcher with different constants baked in for
    indented content, _relative_indent_level tracks how many levels deep the
    renderer currently is inside a NamedParagraph or StructuredList body.
    _wrap_width, _line_separator, and _paragraph_separator are derived from it
    on every access, so _render_node is reused unchanged at every indent level
    -- the same way the parser reuses _parse_flat_content for both top-level
    content and a dedented NamedParagraph body.

    Attributes:
        _line_length (int): Maximum characters per line including indentation.
        _base_indent_level (str): The accumulated indentation string at the
            docstring's own position within the module, supplied by the caller
            and constant for the lifetime of this instance.
        _indent_unit (str): The indentation unit string used in the source file.
        _indent_length (int): Length of _indent_unit.
        _relative_indent_level (int): The nesting depth within the docstring's
            own content, relative to _base_indent_level. 0 while rendering top-
            level content, 1 while inside a NamedParagraph or StructuredList
            body. Mutated only by _nested_body.
    """

    def __init__(
        self,
        line_length: int,
        current_indent: str,
        indent_unit: str,
    ) -> None:
        """Initialises the DocstringRendererBase.

        Args:
            line_length (int): Maximum characters per line including
                indentation.
            current_indent (str): The accumulated indentation string at the
                current nesting level.
            indent_unit (str): The indentation unit string used in the source
                file.
        """
        self._line_length = line_length
        self._base_indent_level = current_indent
        self._indent_unit = indent_unit

        self._indent_length = len(self._indent_unit)
        self._relative_indent_level = 0

    @abstractmethod
    def _render_section_header(self, name: str) -> str:
        """Renders a section header line (or lines) for a NamedParagraph or
        StructuredList section.

        Called with _relative_indent_level at the level the section itself sits
        at (never inside its own body), so implementations that need to insert a
        manual newline within the header -- e.g. NumPy's dashed underline -- can
        use self._base_indent_level directly to align it.

        Args:
            name (str): The section keyword or header text, e.g. 'Args' or
                'Parameters'.

        Returns:
            header (str): The fully rendered header, ready to be followed
                directly by the section body on the next indented line.
        """
        ...

    @abstractmethod
    def _render_structured_list_entry(
        self, entry: StructuredListParameter | StructuredListError
    ) -> str:
        """Renders a single structured list entry to its final, wrapped and
        indented string form.

        Called with _relative_indent_level at whatever level entries actually
        render at for this style -- see _structured_list_entries_indented.
        Implementations needing a further nested level for their own shape (e.g.
        NumPy's indented description) enter another _nested_body block
        themselves.

        Must handle both StructuredListParameter and StructuredListError,
        regardless of whether the implementation's own parser ever produces the
        latter -- see the class docstring.

        Args:
            entry (StructuredListParameter | StructuredListError): A single
                parsed entry.

        Returns:
            rendered (str): The fully rendered, indented entry string.
        """
        ...

    @property
    @abstractmethod
    def _section_body_indented(self) -> bool:
        """Whether a section's body renders one level deeper than its header, or
        flush with it. Applies to both a NamedParagraph's body and a
        StructuredList's entries -- confirmed empirically to behave the same way
        for both, in both currently supported styles.

        Google: True -- both 'Note:' bodies and 'Args:' items are indented under
        their header. NumPy: False -- confirmed against numpy's own docstrings,
        both a Notes body and Parameters entries share a column with their
        header; only a structured list entry's own description (handled inside
        _render_structured_list_entry) indents deeper.

        TODO: if a future style needs these two to differ, split this into two
        separate hooks. Not done now since no supported style needs it.

        Returns:
            result (bool): True if the section body sits one level deeper than
                its header.
        """
        ...

    @property
    def _relative_indent(self) -> str:
        """The indentation string for content at the current relative indent
        level.

        Returns:
            relative_indent (str): The base indent plus one indent unit per
                level of relative nesting.
        """
        relative_indent = (
            self._base_indent_level + self._relative_indent_level * self._indent_unit
        )

        return relative_indent

    @property
    def _wrap_width(self) -> int:
        """Maximum content width at the current relative indent level.

        Returns:
            wrap_width (int): Maximum content width after accounting for the
                base indent and any relative nesting depth.
        """
        wrap_width = self._line_length - len(self._relative_indent)

        return wrap_width

    @property
    def _line_separator(self) -> str:
        """Separator inserted between rendered lines at the current relative
        indent level.

        Returns:
            line_separator (str): A newline followed by the indentation for the
                current relative indent level.
        """
        line_separator = "\n" + self._relative_indent

        return line_separator

    @property
    def _paragraph_separator(self) -> str:
        """Separator inserted between rendered paragraphs at the current
        relative indent level.

        Returns:
            paragraph_separator (str): A blank line followed by the indentation
                for the current relative indent level.
        """
        paragraph_separator = "\n\n" + self._relative_indent

        return paragraph_separator

    @contextmanager
    def _nested_body(self) -> Iterator[None]:
        """Increments _relative_indent_level for the duration of a with block,
        decrementing it again on exit.

        Used when entering a NamedParagraph or StructuredList body, so that
        _wrap_width, _line_separator, and _paragraph_separator all reflect the
        extra indentation for every node rendered inside the block, without
        _render_node needing a separate indented variant of itself. The
        decrement happens in a finally clause so the level is restored even if
        rendering a body node raises.
        """
        self._relative_indent_level += 1

        try:
            yield
        finally:
            self._relative_indent_level -= 1

    def _opens_with_block(self, ir: list[DocstringNode]) -> bool:
        """Determines whether the rendered docstring must start with a leading
        newline.

        A structural block -- CodeBlock, CodeREPL, SimpleList, StructuredList,
        or NamedParagraph -- cannot follow the opening triple quotes on the same
        line. The first node's type alone determines this, so no rendered text
        needs inspecting for fence markers, REPL prompts, list markers, or
        section keywords.

        Args:
            ir (list[DocstringNode]): Fully parsed and typed IR from a parser.

        Returns:
            result (bool): True if a leading newline must be inserted before the
                first node.
        """
        result = bool(ir) and not isinstance(ir[0], Paragraph)

        return result

    def _join_rendered_nodes(
        self, nodes: list[DocstringNode], rendered_parts: list[str]
    ) -> str:
        """Joins rendered node strings, choosing a separator per junction.

        Every junction uses the paragraph separator, except the one immediately
        before a SimpleList with has_leading_blank_line=False, which uses the
        line separator instead. This is the one place a paragraph and a
        following list must render with no blank line between them, mirroring
        how they appeared in the source. Reused at both call sites -- the top-
        level render() and _render_named_paragraph -- rather than duplicating
        the per-junction logic in each.

        Args:
            nodes (list[DocstringNode]): The IR nodes corresponding to
                rendered_parts, in the same order.
            rendered_parts (list[str]): Each node's rendered string form, in
                order.

        Returns:
            joined (str): The fully joined string.
        """
        if not rendered_parts:
            return ""

        joined = rendered_parts[0]

        for node, part in zip(nodes[1:], rendered_parts[1:]):
            separator = (
                self._line_separator
                if isinstance(node, SimpleList) and not node.has_leading_blank_line
                else self._paragraph_separator
            )
            joined += separator + part

        return joined

    def _render_named_paragraph(self, section: NamedParagraph) -> str:
        """Renders a NAMED_PARAGRAPH section, rendering each body node
        independently.

        Whether the body renders one level deeper than the header (Google) or
        flush with it (NumPy) is style-specific -- see _section_body_indented.
        nullcontext stands in for _nested_body when the body stays flush, so
        every node dispatched through _render_node still picks up the correct
        wrap width and separators for whichever level applies, without a
        separate indented dispatcher.

        Args:
            section (NamedParagraph): A parsed named paragraph node.

        Returns:
            rendered (str): The rendered named paragraph string.
        """
        nested_context = (
            self._nested_body() if self._section_body_indented else nullcontext()
        )

        with nested_context:
            rendered_body_nodes = [self._render_node(node) for node in section.body]
            body = self._join_rendered_nodes(section.body, rendered_body_nodes)

        body_indent = self._indent_unit if self._section_body_indented else ""
        header = self._render_section_header(section.header)
        rendered = header + "\n" + self._base_indent_level + body_indent + body

        return rendered

    def _render_simple_list(self, section: SimpleList) -> str:
        """Renders a SIMPLE_LIST section by rendering each parsed item
        independently.

        Each item is wrapped using format_text with a subsequent indent derived
        from the list marker width. For unordered lists this is always 2 spaces
        ('- '). For ordered lists it is derived from the total number of items,
        since longer lists produce wider markers (e.g. '10. ' vs '1. ').

        Reads self._wrap_width and self._line_separator directly rather than
        taking them as parameters. Both are already correct for wherever this
        method is called from: a SimpleList rendered at the top level picks up
        the base values, and one nested inside a NamedParagraph body picks up
        the indented values, since _nested_body has already incremented
        _relative_indent_level by the time this method runs.

        Args:
            section (SimpleList): A parsed simple list node.

        Returns:
            rendered (str): The rendered list string.
        """
        if section.list_type == "unordered":
            marker_width = len(UNORDERED_LIST_MARKER)
            formatted_items = [
                f"{UNORDERED_LIST_MARKER}{item}" for item in section.items
            ]
        else:
            marker_width = len(str(len(section.items))) + len(ORDERED_LIST_SEPARATOR)
            formatted_items = [
                f"{index + 1}{ORDERED_LIST_SEPARATOR}{item}"
                for index, item in enumerate(section.items)
            ]

        subsequent_indent = " " * marker_width

        rendered_items = [
            format_text(
                text=item,
                wrap_width=self._wrap_width,
                line_separator=self._line_separator,
                subsequent_indent=subsequent_indent,
            )
            for item in formatted_items
        ]

        rendered = self._line_separator.join(rendered_items)

        return rendered

    def _render_structured_list(self, section: StructuredList) -> str:
        """Renders a STRUCTURED_LIST section by rendering each entry and
        reassembling.

        Whether entries render one level deeper than the header (Google) or
        flush with it (NumPy) is style-specific -- see _section_body_indented.
        nullcontext stands in for _nested_body when entries stay flush, so the
        render-and-join logic below doesn't need to be duplicated per branch.

        Args:
            section (StructuredList): A parsed structured list node.

        Returns:
            rendered (str): The rendered structured list string.
        """
        nested_context = (
            self._nested_body() if self._section_body_indented else nullcontext()
        )

        with nested_context:
            rendered_entries = [
                self._render_structured_list_entry(entry) for entry in section.entries
            ]
            body = self._line_separator.join(rendered_entries)

        entries_indent = self._indent_unit if self._section_body_indented else ""
        header = self._render_section_header(section.keyword)
        rendered = header + "\n" + self._base_indent_level + entries_indent + body

        return rendered

    def _render_code_block(self, section: CodeBlock) -> str:
        """Renders a CODE_BLOCK section, wrapping content in its original fence
        delimiter.

        Uses self._relative_indent, which already reflects whichever level this
        code block sits at -- top-level or nested inside a NamedParagraph body
        -- so this single method serves both cases.

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
            + self._relative_indent
            + rendered_content
            + "\n"
            + self._relative_indent
            + section.delimiter
        )

        return rendered

    def _render_node(self, node: DocstringNode) -> str:
        """Dispatches a single IR node to the appropriate renderer.

        StructuredList and NamedParagraph are only valid at the top level --
        neither is permitted to nest inside a NamedParagraph body, since none of
        the supported styles allow a second level of named sections. This is
        enforced here as a guard clause rather than relying solely on the parser
        never producing such a shape, since _render_node is now called
        recursively for body content from _render_named_paragraph itself.

        Args:
            node (DocstringNode): Any IR node.

        Returns:
            rendered (str): The rendered node string.

        Raises:
            ValueError: If the node is not a recognized DocstringNode subtype,
                or if a StructuredList or NamedParagraph node is encountered
                while already inside a NamedParagraph body.
        """
        if (
            isinstance(node, StructuredList | NamedParagraph)
            and self._relative_indent_level > 0
        ):
            raise ValueError

        if isinstance(node, Paragraph):
            rendered = format_text(
                text=node.content,
                wrap_width=self._wrap_width,
                line_separator=self._line_separator,
            )
        elif isinstance(node, CodeBlock):
            rendered = self._render_code_block(node)
        elif isinstance(node, CodeREPL):
            rendered = format_code(
                text=node.code,
                line_separator=self._line_separator,
            )
        elif isinstance(node, StructuredList):
            rendered = self._render_structured_list(node)
        elif isinstance(node, SimpleList):
            rendered = self._render_simple_list(node)
        elif isinstance(node, NamedParagraph):
            rendered = self._render_named_paragraph(node)
        else:
            raise ValueError

        return rendered

    def _render_opening_paragraph(self, paragraph: str) -> str:
        """Renders the first paragraph, accounting for the opening triple quotes
        offset.

        Args:
            paragraph (str): The first plain text paragraph.

        Returns:
            rendered_paragraph (str): The wrapped paragraph string.
        """
        normalized = re.sub(RE_PATTERN_WHITESPACE, " ", paragraph.strip())
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

    def _render_nodes(self, ir: list[DocstringNode]) -> list[str]:
        """Renders each IR node to its multi-line string form.

        The first node is given special treatment when it is a Paragraph, since
        the opening triple quotes consume space on the first physical line that
        the wrapping must account for -- a concern of document position, not of
        the Paragraph type itself, so it is handled here rather than inside
        _render_node.

        Args:
            ir (list[DocstringNode]): Fully parsed and typed IR from a parser.

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
            ir (list[DocstringNode]): Fully parsed and typed IR from a parser.

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

        normalized = re.sub(RE_PATTERN_WHITESPACE, " ", content.strip()) or " "
        total_length = (
            len(self._base_indent_level)
            + len(normalized)
            + 2 * DOCSTRING_DELIMITER_LENGTH
        )

        if total_length > self._wrap_width:
            return None

        one_line = DOCSTRING_DELIMITER + normalized + DOCSTRING_DELIMITER

        return one_line

    def render(self, ir: list[DocstringNode]) -> str:
        """Renders a parsed docstring IR into a style-specific docstring string.

        Attempts a one-line rendering first, since that is only ever possible
        for an empty IR or a single Paragraph node short enough to fit within
        the wrap width. Every other IR shape renders each node independently,
        joins them with paragraph separators, and wraps the result in triple
        quotes as a multi-line docstring.

        Args:
            ir (list[DocstringNode]): Fully parsed and typed IR from a parser.

        Returns:
            rendered_docstring (str): The fully rendered docstring string.
        """
        one_line = self._render_one_line(ir)

        if one_line is not None:
            return one_line

        rendered_parts = self._render_nodes(ir)
        rendered_content = self._join_rendered_nodes(ir, rendered_parts)

        if self._opens_with_block(ir):
            rendered_content = "\n" + self._base_indent_level + rendered_content

        rendered_docstring = (
            DOCSTRING_DELIMITER
            + rendered_content
            + "\n"
            + self._base_indent_level
            + DOCSTRING_DELIMITER
        )

        return rendered_docstring
