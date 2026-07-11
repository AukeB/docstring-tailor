"""Contains logic for parsing structured list sections of a docstring."""

from docstring_tailor.constants import (
    DOCSTRING_KEYWORD_SEPARATOR,
    GOOGLE_RAISES_SECTIONS,
    RE_PATTERN_STRUCTURED_LIST_NAME_AND_TYPE,
    STRUCTURED_LIST_DESCRIPTION_SEPARATOR,
)
from docstring_tailor.ir_model import (
    StructuredList,
    StructuredListError,
    StructuredListParameter,
)
from docstring_tailor.utils.utils_parsing import extract_items


class StructuredListParser:
    """Parses raw structured-list section content into a StructuredList node.

    Determines whether the section is a Raises section or a parameter section
    based on the keyword on the first line, then parses each item accordingly.
    """

    def __init__(self) -> None:
        """Initialises the StructuredListParser."""
        pass

    def _parse_parameter_item(self, item: str) -> StructuredListParameter:
        """Parses a single parameter item string into a StructuredListParameter.

        Splits on the first ':' to separate the name/type from the description,
        then matches the name/type portion against the "name (type)" shape. If
        it matches, both name and type are extracted. If it doesn't -- as is
        conventional for Returns/Yields entries, which document only the type --
        the entire name/type portion is treated as the type, and the name is
        left as None.

        Args:
            item (str): A single joined item string.

        Returns:
            parameter (StructuredListParameter): The parsed parameter entry.
        """
        colon_index = item.index(STRUCTURED_LIST_DESCRIPTION_SEPARATOR)
        name_and_type = item[:colon_index].strip()
        description = item[colon_index + 1 :].strip()

        match = RE_PATTERN_STRUCTURED_LIST_NAME_AND_TYPE.match(name_and_type)

        if match:
            name = match.group("name")
            variable_type = match.group("type").strip()
        else:
            name = None
            variable_type = name_and_type

        parameter = StructuredListParameter(
            name=name,
            type=variable_type,
            description=description,
        )

        return parameter

    def _parse_error_item(self, item: str) -> StructuredListError:
        """Parses a single error item string into a StructuredListError.

        Splits on the first ':' to separate the error type from the description.

        Args:
            item (str): A single joined item string.

        Returns:
            error (StructuredListError): The parsed error entry.
        """
        colon_index = item.index(STRUCTURED_LIST_DESCRIPTION_SEPARATOR)
        error_type = item[:colon_index].strip()
        description = item[colon_index + 1 :].strip()

        error = StructuredListError(
            error_type=error_type,
            description=description,
        )

        return error

    def parse(self, content: str) -> StructuredList:
        """Parses raw structured-list section content into a StructuredList
        node.

        Determines the section type from the keyword on the first line, then
        delegates to the appropriate item parser.

        Args:
            content (str): The raw text of a structured-list section, including
                its keyword header line (e.g. 'Args:\\n x (int): ...').

        Returns:
            structured_list (StructuredList): Fully parsed structured list node.
        """
        keyword = content.splitlines()[0].strip().rstrip(DOCSTRING_KEYWORD_SEPARATOR)
        items = extract_items(content, skip_first_line=True)

        entries = (
            [self._parse_error_item(item) for item in items]
            if keyword in GOOGLE_RAISES_SECTIONS
            else [self._parse_parameter_item(item) for item in items]
        )

        structured_list = StructuredList(
            keyword=keyword,
            entries=entries,
        )

        return structured_list
