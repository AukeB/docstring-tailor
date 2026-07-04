"""Contains logic for parsing docstrings into a structured IR."""

from typing import cast

from docstring_tailor.defaults.constants import (
    DOCSTRING_DELIMITER_LENGTH,
    PYTHON_REPL_PREFIX_START,
    RE_PATTERN_BLANK_LINES,
    RE_PATTERN_FENCE,
)
from docstring_tailor.defaults.docstring_keywords import (
    GOOGLE_NAMED_PARAGRAPH_SECTIONS,
    GOOGLE_STRUCTURED_LIST_SECTIONS,
)
from docstring_tailor.defaults.ir_model import (
    CodeBlock,
    CodeBlockDelimiterType,
    CodeREPL,
    DocstringNode,
    NamedParagraph,
    Paragraph,
    SimpleList,
    Unidentified,
)
from docstring_tailor.parser.docstring_section_parser import StructuredListParser
from docstring_tailor.utils.utils_list_detection import get_list_type, is_list
from docstring_tailor.utils.utils_parsing import extract_items, strip_list_marker


class DocstringParser:
    """Parses a raw docstring string into a typed intermediate representation.

    The parsing pipeline proceeds in stages, applied via `_parse_body`:

    1. Wrap the content in a single Unidentified node.
    2. Extract code blocks protected by fence delimiters.
    3. Split remaining Unidentified nodes on blank lines.
    4. Detect and eagerly parse, in order: named paragraphs, structured lists, REPL blocks, and
       simple lists.
    5. Relabel anything still Unidentified as a Paragraph.

    `_parse_body` is applied recursively to the body of a NAMED_PARAGRAPH node (e.g. Note,
    Warning), since that body is itself just docstring content. Named paragraphs and structured
    lists are disallowed from that recursive call, since neither is permitted to nest inside a
    named paragraph's body (a Note can't contain another Note or an Args section).
    """

    def __init__(self) -> None:
        """Initialises the DocstringParser."""
        self._structured_list_parser = StructuredListParser()

    def parse(self, content: str) -> list[DocstringNode]:
        """Parses a raw docstring into a typed IR.

        Args:
            content (str): Raw docstring string including triple-quote delimiters.

        Returns:
            ir (list[DocstringNode]): Fully parsed and typed IR.
        """
        stripped_content = content[
            DOCSTRING_DELIMITER_LENGTH:-DOCSTRING_DELIMITER_LENGTH
        ].strip()

        ir = self._parse_body(
            stripped_content,
            allow_named_paragraph=True,
            allow_structured_list=True,
        )

        return ir

    def _parse_body(
        self,
        content: str,
        *,
        allow_named_paragraph: bool,
        allow_structured_list: bool,
    ) -> list[DocstringNode]:
        """Runs the full classification-and-parsing pipeline over a chunk of docstring content.

        Used both for the top-level docstring body and, recursively, for the body of a
        NAMED_PARAGRAPH node. The two `allow_*` flags are required (no defaults) so every call
        site must state explicitly whether nesting is permitted, rather than relying on a default
        that could silently reintroduce nested Notes or nested Args sections.

        Args:
            content (str): Raw text content to parse (no triple-quote delimiters).
            allow_named_paragraph (bool): Whether to detect and parse NAMED_PARAGRAPH sections.
            allow_structured_list (bool): Whether to detect and parse STRUCTURED_LIST sections.

        Returns:
            ir (list[DocstringNode]): Fully parsed and typed IR for this chunk of content.
        """
        nodes: list[DocstringNode] = [Unidentified(content=content)]

        nodes = self._detect_code_blocks(nodes)
        nodes = self._split_on_blank_lines(nodes)

        if allow_named_paragraph:
            nodes = self._detect_named_paragraphs(nodes)

        if allow_structured_list:
            nodes = self._detect_structured_lists(nodes)

        nodes = self._detect_code_repl(nodes)
        nodes = self._detect_simple_lists(nodes)
        nodes = self._relabel_unidentified_as_paragraph(nodes)

        return nodes

    def _detect_named_paragraphs(
        self,
        nodes: list[DocstringNode],
    ) -> list[DocstringNode]:
        """Identifies NAMED_PARAGRAPH nodes and eagerly parses their body via recursion.

        A node is a named paragraph if its first line matches a keyword such as Note, Notes,
        References, See Also, Warning, or Warnings. The remaining lines are re-parsed by calling
        `_parse_body` recursively, with named paragraphs and structured lists disallowed for that
        call so a Note cannot itself contain another Note or an Args section (matching Google
        docstring convention).

        Args:
            nodes (list[DocstringNode]): Current IR.

        Returns:
            result (list[DocstringNode]): IR with NAMED_PARAGRAPH nodes detected and parsed.
        """
        result: list[DocstringNode] = []

        for node in nodes:
            if not isinstance(node, Unidentified):
                result.append(node)
                continue

            lines = node.content.splitlines()
            first_line = lines[0].strip()
            header = first_line.rstrip(":")

            if header not in GOOGLE_NAMED_PARAGRAPH_SECTIONS:
                result.append(node)
                continue

            body_content = "\n".join(lines[1:])
            body = self._parse_body(
                body_content,
                allow_named_paragraph=False,  # Notes don't nest inside Notes.
                allow_structured_list=False,  # Args/Raises don't belong inside a Note.
            )

            result.append(NamedParagraph(header=header, body=body))

        return result

    def _detect_structured_lists(
        self,
        nodes: list[DocstringNode],
    ) -> list[DocstringNode]:
        """Identifies STRUCTURED_LIST nodes and eagerly parses them into StructuredList nodes.

        A node is a structured list if its first line matches a Google-style keyword such as
        Args, Returns, or Raises. Entry parsing is delegated to StructuredListParser.

        Args:
            nodes (list[DocstringNode]): Current IR.

        Returns:
            result (list[DocstringNode]): IR with StructuredList nodes detected and parsed.
        """
        result: list[DocstringNode] = []

        for node in nodes:
            if not isinstance(node, Unidentified):
                result.append(node)
                continue

            first_line = node.content.splitlines()[0].strip()

            if first_line.rstrip(":") in GOOGLE_STRUCTURED_LIST_SECTIONS:
                result.append(self._structured_list_parser.parse(node.content))
            else:
                result.append(node)

        return result

    def _detect_code_repl(
        self,
        nodes: list[DocstringNode],
    ) -> list[DocstringNode]:
        """Identifies CODE_REPL nodes and parses them into CodeREPL nodes.

        A node is CODE_REPL if its first line starts with the >>> prompt.

        Args:
            nodes (list[DocstringNode]): Current IR.

        Returns:
            result (list[DocstringNode]): IR with CodeREPL nodes detected and parsed.
        """
        result: list[DocstringNode] = []

        for node in nodes:
            if not isinstance(node, Unidentified):
                result.append(node)
                continue

            first_line = node.content.splitlines()[0].strip()

            if first_line.startswith(PYTHON_REPL_PREFIX_START):
                result.append(CodeREPL(code=node.content))
            else:
                result.append(node)

        return result

    def _detect_simple_lists(
        self,
        nodes: list[DocstringNode],
    ) -> list[DocstringNode]:
        """Identifies SIMPLE_LIST nodes and eagerly parses them into SimpleList nodes.

        A node is a simple list if the is_list utility detects at least two list markers at the
        base indentation level.

        Args:
            nodes (list[DocstringNode]): Current IR.

        Returns:
            result (list[DocstringNode]): IR with SimpleList nodes detected and parsed.
        """
        result: list[DocstringNode] = []

        for node in nodes:
            if not isinstance(node, Unidentified):
                result.append(node)
                continue

            if not is_list(node.content):
                result.append(node)
                continue

            list_type = get_list_type(text=node.content)
            items = extract_items(content=node.content)
            stripped_items = [strip_list_marker(item) for item in items]

            result.append(SimpleList(list_type=list_type, items=stripped_items))

        return result

    def _relabel_unidentified_as_paragraph(
        self,
        nodes: list[DocstringNode],
    ) -> list[DocstringNode]:
        """Relabels any remaining Unidentified nodes as Paragraph.

        Acts as the final step in the pipeline, converting anything not identified by a prior
        pass into plain paragraph text.

        Args:
            nodes (list[DocstringNode]): Current IR.

        Returns:
            result (list[DocstringNode]): IR with no remaining Unidentified nodes.
        """
        result = [
            Paragraph(content=node.content) if isinstance(node, Unidentified) else node
            for node in nodes
        ]

        return result

    def _split_on_blank_lines(
        self,
        nodes: list[DocstringNode],
    ) -> list[DocstringNode]:
        """Splits each Unidentified node on blank lines.

        Args:
            nodes (list[DocstringNode]): Current IR.

        Returns:
            result (list[DocstringNode]): New IR with Unidentified nodes split into smaller
                Unidentified chunks.
        """
        result: list[DocstringNode] = []

        for node in nodes:
            if not isinstance(node, Unidentified):
                result.append(node)
                continue

            chunks = RE_PATTERN_BLANK_LINES.split(node.content)

            for chunk in chunks:
                if chunk.strip():
                    result.append(Unidentified(content=chunk.strip()))

        return result

    def _detect_code_blocks(
        self,
        nodes: list[DocstringNode],
    ) -> list[DocstringNode]:
        """Splits Unidentified nodes on code fences, parsing fenced blocks into CodeBlock nodes.

        Each Unidentified node is split using a capturing re.split() on fence delimiters,
        retaining the delimiters as elements. Chunks are iterated with a boolean fence tracker to
        assign the correct node type.

        Args:
            nodes (list[DocstringNode]): Current IR.

        Returns:
            result (list[DocstringNode]): New IR with CodeBlock nodes extracted.
        """
        result: list[DocstringNode] = []

        for node in nodes:
            if not isinstance(node, Unidentified):
                result.append(node)
                continue

            chunks = RE_PATTERN_FENCE.split(node.content)
            in_fence = False
            fence_delimiter: CodeBlockDelimiterType = "```"

            for chunk in chunks:
                fence_match = RE_PATTERN_FENCE.match(chunk)

                if fence_match:
                    if not in_fence:
                        fence_delimiter = cast(CodeBlockDelimiterType, fence_match.group(1))
                    in_fence = not in_fence
                    continue

                if not chunk.strip():
                    continue

                if in_fence:
                    result.append(CodeBlock(code=chunk.strip(), delimiter=fence_delimiter))
                else:
                    result.append(Unidentified(content=chunk.strip()))

        return result