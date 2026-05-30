"""Module for DocstringSectionFormatter."""

import re
import textwrap

from src.docstring_tailor.constants import (
    DOCSTRING_DELIMITER_LENGTH,
    ITEM_SECTIONS,
    LINE_LENGTH,
    PLAIN_SECTIONS,
)


class DocstringSectionFormatter:
    """Formats the content sections of a docstring into the Google Docstring format."""

    def __init__(self, current_indent: str) -> None:
        """
        Initialises the DocstringSectionFormatter.

        Args:
            current_indent (str): The accumulated indentation string at the current nesting level.
        """
        self._current_indent = current_indent

    def _format_plain_paragraph(self, paragraph: str) -> str:
        """
        Formats a plain text paragraph by wrapping it to the configured line length.

        Normalises all internal whitespace to a single space before wrapping, so that
        lines that are too short are correctly joined rather than merged with their
        original indentation intact.

        Args:
            paragraph (str): A plain text paragraph.

        Returns:
            formatted (str): The wrapped paragraph string.
        """
        wrap_width = (
            LINE_LENGTH - DOCSTRING_DELIMITER_LENGTH - len(self._current_indent)
        )
        normalized = re.sub(r"\s+", " ", paragraph.strip())
        lines = textwrap.wrap(normalized, width=wrap_width)
        line_separator = "\n" + self._current_indent
        formatted = line_separator.join(lines)

        return formatted

    def _format_item(self, item_text: str) -> str:
        """
        Formats a single labelled item, wrapping its description if it exceeds the line length.

        Continuation lines are indented one additional level beyond the item's base indent
        by passing a subsequent_indent to textwrap, which is then preserved when the lines
        are joined with the item separator.

        Args:
            item_text (str): The full stripped item string, e.g. 'name (str): Description.'.

        Returns:
            formatted (str): The formatted item string with correct indentation.
        """
        # 4 accounts for the one indent level of the item relative to the section header.
        wrap_width = (
            LINE_LENGTH - len(self._current_indent) - 4
        )  # TODO: Same here, would be perfect if we can determine the number of spaces a single indentation is at the beginning of the program.
        lines = textwrap.wrap(
            item_text.strip(),
            width=wrap_width,
            # Adds 4 spaces to continuation lines; when joined with the item separator
            # (\n + current_indent + 4 spaces), this produces the correct double-indent.
            subsequent_indent="    ",  # TODO: Same here.
        )

        line_separator = "\n" + self._current_indent + "    "  # TODO: Same here.
        formatted = line_separator.join(lines)

        return formatted

    def _parse_items(self, section_content: str) -> list[str]:
        """
        Groups lines from a section body into individual item strings.

        Detects item boundaries by indentation level. A new item starts whenever
        a line returns to the minimum indentation level found in the section.
        Continuation lines at a deeper indentation are joined to the current item.

        Args:
            section_content (str): The section body, excluding the header line.

        Returns:
            items (list[str]): A list of stripped item strings, one per labelled item.
        """
        lines = [line for line in section_content.split("\n") if line.strip()]
        if not lines:
            return []

        base_indent = min(
            len(line) - len(line.lstrip()) for line in lines
        )  # TODO: Wondering if this can be done more efficiently using `self._current_indent`.

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
        """
        Formats the body of an item section by parsing and formatting each item.

        Args:
            section_content (str): The section body, excluding the header line.

        Returns:
            formatted (str): The formatted items joined with the correct indentation.
        """
        item_texts = self._parse_items(section_content=section_content)
        formatted_items = [
            self._format_item(item_text=item_text) for item_text in item_texts
        ]

        item_separator = "\n" + self._current_indent + "    "
        formatted = item_separator.join(formatted_items)

        return formatted

    def _format_item_section(self, section_name: str, section: str) -> str:
        """
        Formats a named section whose body consists of labelled items.

        Strips the section header, formats each item independently, and
        reassembles the section with the header on the first line.

        Args:
            section_name (str): The section header name, e.g. 'Args' or 'Returns'.
            section (str): The full section string including the header line.

        Returns:
            formatted (str): The formatted section string.
        """
        section_content = "\n".join(section.split("\n")[1:])
        formatted_items = self._format_items(section_content=section_content)
        formatted = (
            section_name + ":\n" + self._current_indent + "    " + formatted_items
        )  # TODO: This assumes the indentation is 4 spaces, which is the default and recommended value, but could be different based on user preferences.

        return formatted

    def _format_section(self, section: str) -> str:
        """
        Detects the section type and dispatches to the appropriate formatter.

        Args:
            section (str): A single section of docstring content.

        Returns:
            formatted (str): The formatted section string.
        """
        first_line = section.split("\n")[0].strip().rstrip(":")

        if first_line in ITEM_SECTIONS:
            return self._format_item_section(section_name=first_line, section=section)

        if first_line in PLAIN_SECTIONS:
            section_content = "\n".join(section.split("\n")[1:])
            return (
                first_line
                + ":\n"
                + self._current_indent
                + "    "
                + self._format_plain_paragraph(paragraph=section_content)
            )

        return self._format_plain_paragraph(paragraph=section)

    def format(self, content: str) -> str:
        """
        Formats the full docstring content into the Google Docstring format.

        Splits the content into sections on double newlines, formats each section
        independently, and rejoins them with a blank line between each.

        Args:
            content (str): The stripped docstring content, excluding the triple quote delimiters.

        Returns:
            joined (str): The fully formatted docstring content.
        """
        sections = re.split(r"\n\s*\n", content)
        formatted_sections = [
            self._format_section(section=section) for section in sections
        ]

        paragraph_separator = "\n\n" + self._current_indent
        joined = paragraph_separator.join(formatted_sections)

        return joined
