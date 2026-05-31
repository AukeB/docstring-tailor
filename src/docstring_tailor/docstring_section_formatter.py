"""Module for MultiLineDocstringFormatter."""

import re
import textwrap

from docstring_tailor.constants import (
    DOCSTRING_DELIMITER_LENGTH,
    GOOGLE_ITEM_SECTIONS,
    GOOGLE_PLAIN_SECTIONS,
    GOOGLE_SECTION_HEADERS,
)


class MultiLineDocstringFormatter:
    """Formats the content sections of a docstring into the Google Docstring format.

    The formatting pipeline starts in format(), which delegates to _split_content() to divide the
    docstring into a preamble and a list of named sections. The preamble — everything before the
    first section header — is split on double newlines and each paragraph formatted independently.
    Named sections are dispatched to a dedicated formatter based on their type: item sections (Args,
    Returns, etc.), plain sections (Note, etc.), or code sections (Examples). Code sections are
    preserved verbatim since they contain doctest-format code that must not be wrapped or modified.

    Attributes:
        _line_length (int): Maximum characters per line including indentation and triple double
            quotes.
        _current_indent (str): The accumulated indentation string at the current nesting level,
            updated as the tree is traversed.
        _indent_unit (str): The indentation unit string used in the source file, captured from the
            module node on entry. Initialised to four spaces as a safety placeholder.
        _indent_length (int): The length of the `_ident_unit`, which is the same as the number of
            spaces used for a single indentation.
        _paragraph_separator (str): Paragraphs are separated using two '\n' value and the current
            indentation. Examples of paragraphs are the 'Args' section, or the 'Returns' section.
        _line_separator (str): Lines are separated using a single '\n' value and the current
            indentation. When formatting, this is used for moving something to the next line.
    """

    def __init__(self, line_length: int, current_indent: str, indent_unit: str) -> None:
        """Initialises the MultiLineDocstringFormatter.

        Args:
            line_length (int): Maximum characters per line including indentation.
            current_indent (str): The accumulated indentation string at the current nesting level.
            indent_unit (str): The indentation unit string used in the source file.
        """
        self._line_length = line_length
        self._current_indent = current_indent
        self._indent_unit = indent_unit
        self._indent_length = len(self._indent_unit)

        self._paragraph_separator = "\n\n" + self._current_indent
        self._line_separator = "\n" + self._current_indent

    def _format_plain_paragraph(self, paragraph: str) -> str:
        """Formats a plain text paragraph within an indented section body.

        Used for plain sections such as Note and Warning where the body is indented one level beyond
        the section header. All lines including continuations are at the same indentation level.

        Args:
            paragraph (str): A plain text paragraph.

        Returns:
            formatted_plain_paragraph (str): The wrapped paragraph string.
        """
        normalized = re.sub(r"\s+", " ", paragraph.strip())
        wrap_width = self._line_length - len(self._current_indent) - self._indent_length
        lines = textwrap.wrap(normalized, width=wrap_width)

        line_separator_indented = self._line_separator + self._indent_unit
        formatted_plain_paragraph = line_separator_indented.join(lines)

        return formatted_plain_paragraph

    def _format_plain_section(self, section_name: str, section_body: str) -> str:
        """Formats a plain text section such as Note or Warning.

        Args:
            section_name (str): The section header name, e.g. 'Note'.
            section_body (str): The section content, excluding the header line.

        Returns:
            formatted_plain_section (str): The formatted section string.
        """
        formatted_content = self._format_plain_paragraph(paragraph=section_body)
        formatted_plain_section = (
            section_name
            + ":\n"
            + self._current_indent
            + self._indent_unit
            + formatted_content
        )

        return formatted_plain_section

    def _format_item(self, item_text: str) -> str:
        """Formats a single labelled item, wrapping its description if it exceeds the line length.

        Continuation lines are indented one additional level beyond the item's base indent by
        passing a subsequent_indent to textwrap, which is then preserved when the lines are joined
        with the item separator.

        Args:
            item_text (str): The full stripped item string, e.g. 'name (str): Description.'.

        Returns:
            formatted (str): The formatted item string with correct indentation.
        """
        wrap_width = self._line_length - len(self._current_indent) - self._indent_length
        lines = textwrap.wrap(
            item_text.strip(), width=wrap_width, subsequent_indent=self._indent_unit
        )

        line_separator = "\n" + self._current_indent + self._indent_unit
        formatted = line_separator.join(lines)

        return formatted

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

    def _format_items(self, section_content: str) -> str:
        """Formats the body of an item section by parsing and formatting each item.

        Args:
            section_content (str): The section body, excluding the header line.

        Returns:
            formatted (str): The formatted items joined with the correct indentation.
        """
        item_texts = self._parse_items(section_content=section_content)
        formatted_items = [
            self._format_item(item_text=item_text) for item_text in item_texts
        ]

        item_separator = self._line_separator + self._indent_unit
        formatted_items = item_separator.join(formatted_items)

        return formatted_items

    def _format_item_section(self, section_name: str, section_body: str) -> str:
        """Formats a named section whose body consists of labelled items.

        Formats each item independently and reassembles the section with the header on the first
        line.

        Args:
            section_name (str): The section header name, e.g. 'Args' or 'Returns'.
            section_body (str): The section content, excluding the header line.

        Returns:
            formatted (str): The formatted section string.
        """
        formatted_items = self._format_items(section_content=section_body)
        formatted_item_section = (
            section_name
            + ":\n"
            + self._current_indent
            + self._indent_unit
            + formatted_items
        )

        return formatted_item_section

    def _format_code_section(self, section_name: str, section_body: str) -> str:
        """Formats a code section such as Examples, preserving all content verbatim.

        Doctest-format code must not be wrapped or reformatted. The original indentation is stripped
        and replaced with the correct target indentation for the current nesting level. Blank lines
        between doctest blocks are preserved.

        Args:
            section_name (str): The section header name, e.g. 'Examples'.
            section_body (str): The section content, excluding the header line.

        Returns:
            formatted_code_section (str): The formatted section string with verbatim content.
        """
        lines = section_body.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]

        if not non_empty_lines:
            return section_name + ":"

        base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        target_indent = self._current_indent + self._indent_unit

        formatted_lines: list[str] = []
        for line in lines:
            if line.strip():
                formatted_lines.append(target_indent + line[base_indent:])
            else:
                formatted_lines.append("")

        # Strip leading and trailing blank lines introduced by the split.
        while formatted_lines and not formatted_lines[0].strip():
            formatted_lines.pop(0)
        while formatted_lines and not formatted_lines[-1].strip():
            formatted_lines.pop()

        formatted_code_section = section_name + ":\n" + "\n".join(formatted_lines)

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

        if section_name in GOOGLE_ITEM_SECTIONS:
            return self._format_item_section(
                section_name=section_name, section_body=section_body
            )

        return self._format_code_section(
            section_name=section_name, section_body=section_body
        )

    def _format_middle_paragraph(self, paragraph: str) -> str:
        """Formats a plain text paragraph that appears between the opening paragraph and a section.

        Unlike the opening paragraph, the first line here starts at the full current indentation
        level rather than after the triple quotes, so the full line width is available.

        Args:
            paragraph (str): A plain text paragraph.

        Returns:
            formatted (str): The wrapped paragraph string.
        """
        normalized = re.sub(r"\s+", " ", paragraph.strip())
        wrap_width = self._line_length - len(self._current_indent)
        lines = textwrap.wrap(normalized, width=wrap_width)

        formatted_paragraph = self._line_separator.join(lines)

        return formatted_paragraph

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
        width = self._line_length - len(self._current_indent)
        lines = textwrap.wrap(
            normalized,
            width=width,
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
                    self._format_middle_paragraph(paragraph=paragraph)
                )

        formatted_preamble = self._paragraph_separator.join(formatted_paragraphs)

        return formatted_preamble

    def _split_content(self, content: str) -> tuple[str, list[tuple[str, str]]]:
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

        """Prompt for Claude when I have tokens again: Wondering why you didnt use a dict. Maybe
        because, of some users have the term Note twice in their docstring (even though that does
        not make sense), itw ould fail for dicts and not for the current approach with a list of
        tuples.

        If that's correct, fine, but I think a namedTuple from collections is a slight improvement.
        Do you agree?
        """
        sections: list[tuple[str, str]] = []

        for i, (line_number, section_name) in enumerate(header_positions):
            end = (
                header_positions[i + 1][0]
                if i + 1 < len(header_positions)
                else len(lines)
            )
            section_body = "\n".join(lines[line_number + 1 : end])
            sections.append((section_name, section_body))

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

        for section_name, section_body in sections:
            formatted_parts.append(
                self._format_section(
                    section_name=section_name, section_body=section_body
                )
            )

        formatted_sections = self._paragraph_separator.join(formatted_parts)

        return formatted_sections
