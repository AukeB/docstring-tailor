""" """

import re
import sys

from dataclasses import fields

from docstring_tailor.ir_model import SummaryLine, Paragraph
from docstring_tailor.constants import GOOGLE_SECTION_HEADERS


class GoogleParser:
    """ """

    def __init__(
        self,
        content: str,
    ) -> None:
        """ """
        self.content = content

    def parse_preamble(self, preamble: str):
        preamble_sections = re.split(r"\n\s*\n", preamble.strip())
        paragraphs = []

        for i, section in enumerate(preamble_sections):
            if not section.strip():
                continue
            if i == 0:
                summary_line = SummaryLine(text=section)
            else:
                paragraph = Paragraph(text=section)
                paragraphs.append(paragraph)
            
        if paragraphs:
            return summary_line, paragraphs
        
        return summary_line

    def _split_content(self, content: str):
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
        sections = []

        return preamble

    def parse(self):
        """ """
        preamble = self._split_content(content=self.content)

        preamble_parsed = self.parse_preamble(preamble=preamble)

        print("")
        print(self.content)
        print("")
        print(preamble_parsed)

        sys.exit()