"""Contains logic for parsing docstrings into a structured IR."""

from inspect import cleandoc
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
)
from docstring_tailor.parser.docstring_structured_list_parser import (
    StructuredListParser,
)
from docstring_tailor.utils.utils_list_detection import get_list_type, is_list
from docstring_tailor.utils.utils_parsing import extract_items


class DocstringParser:
    """Parses a raw docstring string into a typed intermediate representation.

    The parsing pipeline operates in two phases:

    1. Indentation-based top-level scanning — identifies keyword-headed sections
       (NamedParagraph, StructuredList) by tracking base indentation, without
       relying on blank lines. This sidesteps the chicken-and-egg problem where
       named paragraphs need blank-line detection to be found, but themselves
       contain blank lines.
    2. Flat content parsing — applies fence detection, blank-line splitting, and
       type classification to non-keyword content, and recursively to named
       paragraph bodies after dedenting.
    """

    def __init__(self) -> None:
        """Initialises the DocstringParser."""
        self._structured_list_parser = StructuredListParser()

    def _parse_simple_list(self, content: str) -> SimpleList:
        """Parses raw list content into a SimpleList node.

        Args:
            content (str): Raw list text including markers.

        Returns:
            simple_list (SimpleList): Parsed simple list with markers stripped
                from items.
        """
        list_type = get_list_type(text=content)
        items = extract_items(content=content)

        simple_list = SimpleList(list_type=list_type, items=items)

        return simple_list

    def _classify_paragraph(self, content: str) -> DocstringNode:
        """Classifies a single blank-line-delimited chunk into its concrete IR
        type.

        Checks for REPL and list patterns before falling back to plain
        Paragraph.

        Args:
            content (str): A single stripped paragraph chunk.

        Returns:
            node (DocstringNode): A CodeREPL, SimpleList, or Paragraph node.
        """
        first_line = content.splitlines()[0].strip()

        if first_line.startswith(PYTHON_REPL_PREFIX_START):
            return CodeREPL(code=content)

        if is_list(content):
            return self._parse_simple_list(content)

        return Paragraph(content=content)

    def _extract_code_blocks(self, content: str) -> list[CodeBlock | str]:
        """Splits content on code fences, preserving fence structure.

        Uses a capturing re.split() so fence delimiter lines are retained as
        elements. Iterates the result with a boolean fence tracker to emit
        CodeBlock nodes for fenced regions and plain strings for everything
        else.

        Args:
            content (str): Raw content that may contain fenced code blocks.

        Returns:
            chunks (list[CodeBlock | str]): CodeBlock nodes and plain string
                segments in document order.
        """
        raw_chunks = RE_PATTERN_FENCE.split(content)
        result: list[CodeBlock | str] = []
        in_fence = False
        fence_delimiter: CodeBlockDelimiterType = "```"

        for chunk in raw_chunks:
            fence_match = RE_PATTERN_FENCE.match(chunk)

            if fence_match:
                fence_delimiter = (
                    cast(CodeBlockDelimiterType, fence_match.group(1))
                    if not in_fence
                    else fence_delimiter
                )
                in_fence = not in_fence
                continue

            if not chunk.strip():
                continue

            if in_fence:
                result.append(CodeBlock(code=chunk.strip(), delimiter=fence_delimiter))
            else:
                result.append(chunk)

        return result

    def _parse_flat_content(self, content: str) -> list[DocstringNode]:
        """Parses flat content (no keyword-headed sections) into typed IR nodes.

        Extracts code blocks first to protect them from blank-line splitting,
        then splits remaining plain strings on blank lines and classifies each
        chunk.

        Args:
            content (str): Raw flat content, already dedented if from a named
                paragraph body.

        Returns:
            nodes (list[DocstringNode]): Parsed IR nodes in document order.
        """
        chunks = self._extract_code_blocks(content)
        nodes: list[DocstringNode] = []

        for chunk in chunks:
            if isinstance(chunk, CodeBlock):
                nodes.append(chunk)
                continue

            for paragraph in RE_PATTERN_BLANK_LINES.split(chunk):
                if paragraph.strip():
                    nodes.append(self._classify_paragraph(paragraph.strip()))

        return nodes

    def _parse_named_paragraph_body(self, content: str) -> list[DocstringNode]:
        """Dedents and parses the indented body of a named paragraph section.

        Strips the shared base indentation from all body lines before delegating
        to _parse_flat_content, so that code fences and list markers appear at
        column zero relative to the body.

        Args:
            content (str): Raw body lines joined as a string, with original
                indentation intact.

        Returns:
            body (list[DocstringNode]): Parsed body nodes.
        """
        lines = content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]

        if not non_empty_lines:
            return []

        base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        dedented = "\n".join(
            line[base_indent:] if line.strip() else "" for line in lines
        )

        body = self._parse_flat_content(dedented)

        return body

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
        header = lines[0].strip().rstrip(":")
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
        keyword = content.splitlines()[0].strip().rstrip(":")

        if keyword in GOOGLE_STRUCTURED_LIST_SECTIONS:
            node = self._structured_list_parser.parse(content)
        else:
            node = self._parse_named_paragraph(content)

        return node

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
        segment.

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
            keyword = line.strip().rstrip(":")
            is_base = indent == base_indent
            is_keyword_line = is_base and (
                keyword in GOOGLE_NAMED_PARAGRAPH_SECTIONS
                or keyword in GOOGLE_STRUCTURED_LIST_SECTIONS
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
