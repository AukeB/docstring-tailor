"""Module for MultiLineDocstringFormatter."""

import re
import textwrap

from docstring_tailor.constants import (
    CODE_BLOCK_PREFIXES,
    DOCSTRING_DELIMITER_LENGTH,
    GOOGLE_CODE_SECTIONS,
    GOOGLE_ITEM_SECTIONS,
    GOOGLE_PLAIN_SECTIONS,
    GOOGLE_SECTION_HEADERS,
    Section,
)
from docstring_tailor.utils.utils_formatting import format_list, format_paragraph
from docstring_tailor.utils.utils_list_detection import is_list


class MultiLineDocstringFormatter:
    """Formats the content sections of a docstring into the Google Docstring format.

    The formatting pipeline starts in format(), which delegates to _split_content() to divide the
    docstring into a preamble and a list of named sections. The preamble — everything before the
    first section header — is split on double newlines and each paragraph formatted independently.
    Named sections are dispatched to a dedicated formatter based on their type: item sections (Args,
    Returns, etc.), plain sections (Note, etc.), or code sections (Examples). Code sections are
    preserved verbatim since they contain doctest-format code that must not be wrapped or modified.

    Attributes:
        _line_length (int): Maximum characters per line including indentation and surrounding triple
            double quotes.
        _current_indent (str): The accumulated indentation string at the current nesting level,
            updated as the tree is traversed.
        _indent_unit (str): The indentation unit string used in the source file, captured from the
            module node on entry. Initialised to four spaces as a safety placeholder.
        _indent_length (int): Length of `_indent_unit`, equivalent to the number of spaces used for
            a single indentation level.
        _paragraph_separator (str): Separator inserted between formatted paragraphs, consisting of
            two newline characters followed by the current indentation.
        _line_separator (str): Separator inserted between formatted lines, consisting of a single
            newline character followed by the current indentation.
        _line_separator_indented (str): Line separator followed by one additional indentation level,
            used when formatting indented content such as section bodies.
        _wrap_width (int): Maximum content width available for wrapping after accounting for the
            current indentation.
        _wrap_width_indented (int): Maximum content width available for wrapping indented content
            after accounting for both the current indentation and one additional indentation level.
    """

    def __init__(
        self,
        line_length: int,
        current_indent: str,
        indent_unit: str,
        detect_lists: bool,
    ) -> None:
        """Initialises the MultiLineDocstringFormatter.

        Args:
            line_length (int): Maximum characters per line including indentation.
            current_indent (str): The accumulated indentation string at the current nesting level.
            indent_unit (str): The indentation unit string used in the source file.
            detect_lists (bool): Whether to detect and preserve list formatting.
        """
        self._line_length = line_length
        self._current_indent = current_indent
        self._indent_unit = indent_unit
        self._detect_lists = detect_lists

        self._indent_length = len(self._indent_unit)

        self._paragraph_separator: str = "\n\n" + self._current_indent
        self._line_separator: str = "\n" + self._current_indent
        self._line_separator_indented: str = self._line_separator + self._indent_unit

        self._wrap_width: int = self._line_length - len(self._current_indent)
        self._wrap_width_indented: int = self._wrap_width - self._indent_length

    def _format_text_block(
        self, text: str, wrap_width: int, line_separator: str
    ) -> str:
        """Formats a plain text block, dispatching to list formatting if a list is detected.

        If detect_lists is enabled and the text is identified as a list, delegates to format_list to
        preserve each item on its own line. Otherwise wraps as a plain paragraph.

        Args:
            text (str): The text block to format.
            wrap_width (int): Maximum number of characters per line.
            line_separator (str): The string used to join lines.

        Returns:
            formatted (str): The formatted text block.
        """
        if self._detect_lists and is_list(text=text):
            formatted = format_list(
                text=text,
                wrap_width=wrap_width,
                line_separator=line_separator,
            )
        else:
            formatted = format_paragraph(
                text=text,
                wrap_width=wrap_width,
                line_separator=line_separator,
            )

        return formatted

    def _format_plain_section(self, section_name: str, section_body: str) -> str:
        """Formats a plain text section such as 'Note' or 'Warning'.

        Args:
            section_name (str): The section header name, e.g. 'Note'.
            section_body (str): The section content, excluding the header line.

        Returns:
            formatted_plain_section (str): The formatted section string.
        """
        formatted_content = self._format_text_block(
            text=section_body,
            wrap_width=self._wrap_width_indented,
            line_separator=self._line_separator_indented,
        )

        formatted_plain_section = (
            section_name
            + ":\n"
            + self._current_indent
            + self._indent_unit
            + formatted_content
        )

        return formatted_plain_section

    def _parse_items(self, section_content: str) -> list[str]:
        """Groups lines from a section body into individual item strings.

        Detects item boundaries by indentation level. A new item starts whenever a line returns to
        the minimum indentation level found in the section. Continuation lines at a deeper
        indentation are joined to the current item.

        Args:
            section_content (str): The section body, excluding the header line.

        Returns:
            items (list[str]): A list of stripped item strings, one per labelled item.
        """
        lines = [line for line in section_content.split("\n") if line.strip()]

        if not lines:
            return []

        base_indent = min(len(line) - len(line.lstrip()) for line in lines)

        items: list[str] = []
        current_item_lines: list[str] = []
        for line in lines:
            indent = len(line) - len(line.lstrip())
            if indent == base_indent and current_item_lines:
                items.append(" ".join(l.strip() for l in current_item_lines))
                current_item_lines = [line]
            else:
                current_item_lines.append(line)

        if current_item_lines:
            items.append(" ".join(l.strip() for l in current_item_lines))

        return items

    def _format_item_section(self, section_name: str, section_body: str) -> str:
        """Formats a named section whose body consists of labelled items.

        Parses the section body into individual items, formats each independently, and reassembles
        the section with the header on the first line.

        Args:
            section_name (str): The section header name, e.g. 'Args' or 'Returns'.
            section_body (str): The section content, excluding the header line.

        Returns:
            formatted_item_section (str): The formatted section string.
        """
        item_texts = self._parse_items(section_content=section_body)

        formatted_items = [
            format_paragraph(
                text=item_text,
                wrap_width=self._wrap_width_indented,
                line_separator=self._line_separator_indented,
                subsequent_indent=self._indent_unit,
            )
            for item_text in item_texts
        ]

        formatted_item_section = (
            section_name
            + ":\n"
            + self._current_indent
            + self._indent_unit
            + self._line_separator_indented.join(formatted_items)
        )

        return formatted_item_section

    def _format_code_chunk(self, chunk: str) -> str:
        """Formats a single verbatim code block by stripping original indentation and re-indenting.

        Preserves the content exactly as written, only adjusting the leading indentation to match
        the current nesting level. Blank lines within the block are preserved.

        Args:
            chunk (str): A single code block string, delimited by double newlines in the caller.

        Returns:
            formatted_code_chunk (str): The re-indented code block with no leading prefix on the
                first line, since the prefix is added by the outer join in _format_code_section.
        """
        lines = chunk.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]

        if not non_empty_lines:
            return ""

        base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)

        formatted_lines: list[str] = []
        for line in lines:
            if line.strip():
                formatted_lines.append(line[base_indent:])
            else:
                formatted_lines.append("")

        while formatted_lines and not formatted_lines[0]:
            formatted_lines.pop(0)
        while formatted_lines and not formatted_lines[-1]:
            formatted_lines.pop()

        formatted_code_chunk = self._line_separator_indented.join(formatted_lines)

        return formatted_code_chunk

    def _format_code_section(
        self,
        section_name: str,
        section_body: str,
        code_block_prefixes: tuple[str, str, str],
    ) -> str:
        """Formats a code-oriented section such as Examples, preserving code verbatim and wrapping
        plain text.

        Splits the section body on double newlines into chunks. A chunk is treated as a code block
        if its first non-empty line starts with ``code_block_prefixes``; otherwise it is treated as
        plain text and formatted with ``_format_plain_paragraph``.

        This distinction cannot be made perfectly — program output that follows a blank line is
        indistinguishable from plain text — but the convention that explanatory text between code
        blocks does not start with the configured code prefix covers all practical cases.

        Args:
            section_name (str): The section header name, e.g. ``'Examples'``.
            section_body (str): The section content, excluding the header line.
            code_block_prefixes (tuple[str, str, str]): Prefixes that identify the start of a code
                block.

        Returns:
            formatted_code_section (str): The formatted section string with verbatim code blocks and
                wrapped plain text.
        """
        chunks = re.split(r"\n\s*\n", section_body)
        formatted_chunks: list[str] = []

        for chunk in chunks:
            if not chunk.strip():
                continue

            first_content_line = next(
                (line.strip() for line in chunk.split("\n") if line.strip()), ""
            )

            if first_content_line.startswith(code_block_prefixes):
                formatted_chunks.append(self._format_code_chunk(chunk=chunk))
            else:
                formatted_chunks.append(
                    self._format_text_block(
                        text=chunk,
                        wrap_width=self._wrap_width_indented,
                        line_separator=self._line_separator_indented,
                    )
                )

        if not formatted_chunks:
            return section_name + ":"

        chunk_separator = self._paragraph_separator + self._indent_unit
        content = chunk_separator.join(formatted_chunks)

        formatted_code_section = (
            section_name + ":\n" + self._current_indent + self._indent_unit + content
        )

        return formatted_code_section

    def _format_section(self, section_name: str, section_body: str) -> str:
        """Detects the section type and dispatches to the appropriate formatter.

        Args:
            section_name (str): The section header name, e.g. 'Args' or 'Examples'.
            section_body (str): The section content, excluding the header line.

        Returns:
            (str): The formatted section string.
        """
        if section_name in GOOGLE_PLAIN_SECTIONS:
            return self._format_plain_section(
                section_name=section_name, section_body=section_body
            )
        elif section_name in GOOGLE_ITEM_SECTIONS:
            return self._format_item_section(
                section_name=section_name, section_body=section_body
            )
        elif section_name in GOOGLE_CODE_SECTIONS:
            return self._format_code_section(
                section_name=section_name,
                section_body=section_body,
                code_block_prefixes=CODE_BLOCK_PREFIXES,
            )
        else:
            raise ValueError(f"Unsupported section_name: {section_name}")

    def _format_opening_paragraph(self, paragraph: str) -> str:
        """Formats the first paragraph of a docstring, which starts after the opening triple double
        quotes.

        Uses initial_indent to simulate the triple quotes consuming space on the first line,
        ensuring it wraps correctly. The placeholder is stripped before returning since the actual
        triple quotes are prepended by the caller.

        Args:
            paragraph (str): The first plain text paragraph.

        Returns:
            formatted_paragraph (str): The wrapped paragraph string.
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

        formatted_paragraph = self._line_separator.join(lines)

        return formatted_paragraph

    def _format_preamble(self, preamble: str) -> str:
        """Formats the preamble — the content before the first named section header.

        Splits on double newlines to separate paragraphs. The first paragraph is formatted with
        _format_opening_paragraph to account for the triple quotes consuming space on the first
        line. Subsequent paragraphs are formatted with _format_middle_paragraph at full line width.

        Args:
            preamble (str): The preamble content string.

        Returns:
            formatted_preamble (str): The formatted preamble string.
        """
        paragraphs = re.split(r"\n\s*\n", preamble.strip())
        formatted_paragraphs: list[str] = []

        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
            if i == 0:
                formatted_paragraphs.append(
                    self._format_opening_paragraph(paragraph=paragraph)
                )
            else:
                formatted_paragraphs.append(
                    self._format_text_block(
                        text=paragraph,
                        wrap_width=self._wrap_width,
                        line_separator=self._line_separator,
                    )
                )

        formatted_preamble = self._paragraph_separator.join(formatted_paragraphs)

        return formatted_preamble

    def _split_content(self, content: str) -> tuple[str, list[Section]]:
        """Splits docstring content into a preamble and a list of named sections.

        Scans the content line by line for section headers from GOOGLE_SECTION_HEADERS. Everything
        before the first header is the preamble. Each header and the lines that follow it up to the
        next header form one section. Section headers are matched with longer names first to avoid
        partial matches (e.g. 'See Also' before 'Also').

        Args:
            content (str): The stripped docstring content, excluding the triple double quote
                delimiters.

        Returns:
            result (tuple[str, list[tuple[str, str]]]): A tuple of the preamble string and a list of
                (section_name, section_body) pairs.
        """
        lines = content.split("\n")

        sorted_headers: list[str] = sorted(
            GOOGLE_SECTION_HEADERS, key=lambda h: len(h), reverse=True
        )

        header_pattern = re.compile(
            r"^\s*(" + "|".join(re.escape(h) for h in sorted_headers) + r"):\s*$"
        )

        header_positions: list[tuple[int, str]] = []

        for i, line in enumerate(lines):
            match = header_pattern.match(line)
            if match:
                header_positions.append((i, match.group(1)))

        if not header_positions:
            return content, []

        preamble = "\n".join(lines[: header_positions[0][0]])
        sections: list[Section] = []

        for i, (line_number, section_name) in enumerate(header_positions):
            end = (
                header_positions[i + 1][0]
                if i + 1 < len(header_positions)
                else len(lines)
            )
            section_body = "\n".join(lines[line_number + 1 : end])
            section = Section(name=section_name, body=section_body)
            sections.append(section)

        return preamble, sections

    def format(self, content: str) -> str:
        """Formats the full docstring content into the Google Docstring format.

        Splits the content into a preamble and named sections by detecting section headers first, so
        that double newlines inside sections such as Examples are not mistakenly treated as
        paragraph breaks. Formats each part independently and rejoins with a blank line between
        each.

        Args:
            content (str): The stripped docstring content, excluding the triple quote delimiters.

        Returns:
            formatted_sections (str): The fully formatted docstring content.
        """
        preamble, sections = self._split_content(content=content)

        formatted_parts: list[str] = []

        if preamble.strip():
            formatted_parts.append(self._format_preamble(preamble=preamble))

        for section in sections:
            formatted_parts.append(
                self._format_section(
                    section_name=section.name, section_body=section.body
                )
            )

        formatted_sections = self._paragraph_separator.join(formatted_parts)

        return formatted_sections
