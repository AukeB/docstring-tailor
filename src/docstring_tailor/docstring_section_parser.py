"""Contains logic for parsing structured list sections of a docstring."""

from docstring_tailor.constants import GOOOGLE_RAISES_SECTIONS
from docstring_tailor.ir_model import (
    DocstringSection,
    ParsedStructuredList,
    SectionType,
    StructuredListError,
    StructuredListParameter,
)

from docstring_tailor.utils.utils_parsing import extract_items


class StructuredListParser:
    """Parses a STRUCTURED_LIST docstring section into typed parameter or error entries.

    Determines whether the section is a Raises section or a parameter section
    based on the keyword on the first line, then parses each item accordingly.
    """

    def __init__(self) -> None:
        """Initialises the StructuredListParser."""
        pass

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
        items = extract_items(section.content, skip_first_line=True)

        if keyword in GOOOGLE_RAISES_SECTIONS:
            entries = [self._parse_error_section(item) for item in items]
        else:
            entries = [self._parse_parameter_section(item) for item in items]

        parsed = ParsedStructuredList(
            section_type=SectionType.STRUCTURED_LIST,
            entries=entries,
        )

        return parsed