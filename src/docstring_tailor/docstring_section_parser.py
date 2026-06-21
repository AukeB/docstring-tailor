"""Contains logic for parsing structured list sections of a docstring."""

from docstring_tailor.constants import GOOOGLE_RAISES_SECTIONS
from docstring_tailor.ir_model import (
    DocstringSection,
    ParsedStructuredList,
    SectionType,
    StructuredListError,
    StructuredListParameter,
)


class StructuredListParser:
    """Parses a STRUCTURED_LIST docstring section into typed parameter or error entries.

    Determines whether the section is a Raises section or a parameter section
    based on the keyword on the first line, then parses each item accordingly.
    """

    def __init__(self) -> None:
        """Initialises the StructuredListParser."""
        pass

    def _extract_items(self, section: DocstringSection) -> list[str]:
        """Extracts individual item strings from a structured list section.

        Items are detected by indentation — lines at the base indentation level
        start a new item, and continuation lines at a deeper indentation are
        joined to the preceding item.

        Args:
            section (DocstringSection): A STRUCTURED_LIST section.

        Returns:
            items (list[str]): Each item as a single joined string.
        """
        lines = section.content.splitlines()

        lines = lines[1:]
        non_empty_lines = [line for line in lines if line.strip()]
        base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)

        items: list[str] = []
        current_item_lines: list[str] = []

        for line in lines:
            current_indent = len(line) - len(line.lstrip())

            if current_indent == base_indent and current_item_lines:
                first_line = current_item_lines[0].strip()
                continuation = " ".join(l.strip() for l in current_item_lines[1:])
                items.append(f"{first_line} {continuation}".strip())
                current_item_lines = [line]
            else:
                current_item_lines.append(line)

        if current_item_lines:
            first_line = current_item_lines[0].strip()
            continuation = " ".join(l.strip() for l in current_item_lines[1:])
            items.append(f"{first_line} {continuation}".strip())

        return items

    def _parse_parameter_section(self, item: str) -> StructuredListParameter:
        """Parses a single parameter item string into a StructuredListParameter.

        Splits on the first ':' to separate the name/type from the description,
        then searches backwards from that ':' for the last ')' to extract the type.

        Args:
            item (str): A single joined item string.

        Returns:
            parameter (StructuredListParameter): The parsed parameter entry.
        """
        colon_index = item.index(":")
        name_and_type = item[:colon_index]
        description = item[colon_index + 1 :].strip()

        opening_parenthesis_index = name_and_type.index("(")
        closing_parenthesis_index = name_and_type.rindex(")")

        name = name_and_type[:opening_parenthesis_index].strip()
        variable_type = name_and_type[
            opening_parenthesis_index + 1 : closing_parenthesis_index
        ].strip()

        parameter = StructuredListParameter(
            name=name,
            type=variable_type,
            description=description,
        )

        return parameter

    def _parse_error_section(self, item: str) -> StructuredListError:
        """Parses a single error item string into a StructuredListError.

        Splits on the first ':' to separate the error type from the description.

        Args:
            item (str): A single joined item string.

        Returns:
            error (StructuredListError): The parsed error entry.
        """
        colon_index = item.index(":")
        error_type = item[:colon_index].strip()
        description = item[colon_index + 1 :].strip()

        error = StructuredListError(
            error_type=error_type,
            description=description,
        )

        return error

    def parse(self, section: DocstringSection) -> ParsedStructuredList:
        """Parses a STRUCTURED_LIST section into a ParsedStructuredList node.

        Determines the section type from the keyword on the first line, then
        delegates to the appropriate item parser.

        Args:
            section (DocstringSection): A STRUCTURED_LIST section to parse.

        Returns:
            parsed (ParsedStructuredList): Fully parsed structured list node.
        """
        keyword = section.content.splitlines()[0].strip().rstrip(":")
        items = self._extract_items(section)

        if keyword in GOOOGLE_RAISES_SECTIONS:
            entries = [self._parse_error_section(item) for item in items]
        else:
            entries = [self._parse_parameter_section(item) for item in items]

        parsed = ParsedStructuredList(
            section_type=SectionType.STRUCTURED_LIST,
            entries=entries,
        )

        return parsed
