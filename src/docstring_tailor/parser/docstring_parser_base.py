"""Contains the abstract base parser shared by all docstring styles.

Holds the style-agnostic flat-content parsing pipeline -- the part that turns
raw prose into Paragraph, CodeBlock, CodeREPL, and SimpleList nodes -- together
with the single abstract parse() contract every style parser must fulfil.

This is deliberately the lower of two abstraction layers. IndentationBasedParser
extends this base with heading-and-indentation section detection (Google,
NumPy), while directive-based styles (Sphinx, later Epydoc) extend the same base
with their own directive/field scanning. Both grammars reuse the flat-content
pipeline here unchanged for any content that is not a keyword- or directive-
headed section -- code blocks, prose paragraphs, and simple lists all classify
identically regardless of the surrounding style.
"""

from abc import ABC, abstractmethod
from typing import cast

from docstring_tailor.constants import (
    CODE_REPL_PROMPT,
    RE_PATTERN_BLANK_LINES,
    RE_PATTERN_CODE_BLOCK_DELIMITER,
)
from docstring_tailor.ir_model import (
    CodeBlock,
    CodeBlockDelimiterType,
    CodeREPL,
    DocstringNode,
    Paragraph,
    SimpleList,
)
from docstring_tailor.utils.utils_formatting import get_indent
from docstring_tailor.utils.utils_list_detection import find_list_start, get_list_type
from docstring_tailor.utils.utils_parsing import extract_items


class DocstringParserBase(ABC):
    """Abstract base for every docstring-style parser.

    Provides the flat-content classification pipeline (_parse_flat_content and
    its helpers) shared by all styles, and declares the single abstract parse()
    method each concrete style parser must implement. Section detection itself
    -- how keyword or directive sections are found and split off from flat
    content -- is intentionally left out of this base, since that is exactly
    where docstring styles diverge; it belongs to the intermediate layer
    (IndentationBasedParser) or the concrete parser (SphinxDocstringParser).
    """

    @abstractmethod
    def parse(self, content: str) -> list[DocstringNode]:
        """Parses a raw docstring string into a typed IR.

        Args:
            content (str): Raw docstring string including triple-quote
                delimiters.

        Returns:
            ir (list[DocstringNode]): Fully parsed and typed IR.
        """

        ...

    def _parse_simple_list(
        self, content: str, has_leading_blank_line: bool
    ) -> SimpleList:
        """Parses raw list content into a SimpleList node.

        Args:
            content (str): Raw list text including markers.
            has_leading_blank_line (bool): Whether the list was preceded by a
                blank line in the source, as determined by the caller's position
                within the chunk.

        Returns:
            simple_list (SimpleList): Parsed simple list with markers stripped
                from items.
        """

        list_type = get_list_type(text=content)
        items = extract_items(content=content)

        simple_list = SimpleList(
            list_type=list_type,
            items=items,
            has_leading_blank_line=has_leading_blank_line,
        )

        return simple_list

    def _classify_chunk(self, content: str) -> list[DocstringNode]:
        """Classifies a single blank-line-delimited chunk into one or more IR
        nodes.

        Checks for the REPL pattern on the whole chunk first, same as before.
        Otherwise, uses find_list_start to locate where a confirmed list run
        begins within the chunk, if at all. A chunk with no list run yields a
        single Paragraph. A chunk that is a list run from its very first line
        yields a single SimpleList with has_leading_blank_line=True, since
        nothing in this chunk precedes it -- it was already separated from
        whatever came before by the outer blank-line split (or it is the first
        node overall). A chunk where a list run starts partway through yields
        two nodes: the leading Paragraph, then a SimpleList with
        has_leading_blank_line=False, since that list immediately follows the
        paragraph with no blank line between them.

        Args:
            content (str): A single stripped paragraph chunk.

        Returns:
            nodes (list[DocstringNode]): One node for a plain Paragraph or
                CodeREPL chunk, or a Paragraph followed by a SimpleList when a
                list run immediately follows leading prose within the chunk.
        """

        first_line = content.splitlines()[0].strip()

        if first_line.startswith(CODE_REPL_PROMPT):
            code_repl = CodeREPL(code=content)

            nodes: list[DocstringNode] = [code_repl]

            return nodes

        list_start = find_list_start(content)

        if list_start is None:
            paragraph = Paragraph(content=content)

            nodes: list[DocstringNode] = [paragraph]

            return nodes

        if list_start == 0:
            simple_list = self._parse_simple_list(
                content=content, has_leading_blank_line=True
            )

            nodes: list[DocstringNode] = [simple_list]

            return nodes

        lines = content.split("\n")
        paragraph_content = "\n".join(lines[:list_start]).strip()
        list_content = "\n".join(lines[list_start:])

        paragraph = Paragraph(content=paragraph_content)

        simple_list = self._parse_simple_list(
            content=list_content, has_leading_blank_line=False
        )

        nodes: list[DocstringNode] = [paragraph, simple_list]

        return nodes

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

        raw_chunks = RE_PATTERN_CODE_BLOCK_DELIMITER.split(content)
        result: list[CodeBlock | str] = []
        open_delimiter: CodeBlockDelimiterType | None = None

        for chunk in raw_chunks:
            fence_match = RE_PATTERN_CODE_BLOCK_DELIMITER.match(chunk)

            if fence_match:
                if open_delimiter is None:
                    delimiter_text = fence_match.group(1)
                    open_delimiter = cast(CodeBlockDelimiterType, delimiter_text)
                else:
                    open_delimiter = None

                continue

            if not chunk.strip():
                continue

            if open_delimiter is None:
                result.append(chunk)
            else:
                stripped_code = chunk.strip()
                code_block = CodeBlock(code=stripped_code, delimiter=open_delimiter)

                result.append(code_block)

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
                    stripped_paragraph = paragraph.strip()
                    classified_nodes = self._classify_chunk(stripped_paragraph)

                    nodes.extend(classified_nodes)

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
            empty_body: list[DocstringNode] = []

            return empty_body

        indents = [get_indent(line) for line in non_empty_lines]
        base_indent = min(indents)

        dedented_lines = [line[base_indent:] if line.strip() else "" for line in lines]
        dedented = "\n".join(dedented_lines)

        body = self._parse_flat_content(dedented)

        return body
