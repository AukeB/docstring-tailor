"""Contains the abstract base class for structured list section parsers."""

from abc import ABC, abstractmethod

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
from docstring_tailor.utils.utils_parsing import extract_items, extract_structured_items


class StructuredListParserBase(ABC):
    """Base class for style-specific structured list section parsers.

    Mirrors DocstringNode in the IR model: a thin contract enforcing the one
    method every style- specific parser must implement, with no shared
    behaviour. Google and NumPy's item syntax differs too much (inline 'name
    (type):' vs. header/description on separate lines) to usefully share parsing
    logic below this level.
    """

    @abstractmethod
    def parse(self, content: str) -> StructuredList:
        """Parses raw structured-list section content into a StructuredList
        node.

        Args:
            content (str): The raw text of a structured-list section, including
                its keyword header line.

        Returns:
            structured_list (StructuredList): Fully parsed structured list node.
        """
        ...


class GoogleStructuredListParser(StructuredListParserBase):
    """Parses raw structured-list section content into a StructuredList node.

    Determines whether the section is a Raises section or a parameter section
    based on the keyword on the first line, then parses each item accordingly.
    """

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


class NumpyStructuredListParser(StructuredListParserBase):
    """Parses raw NumPy-style structured-list section content into a
    StructuredList node.

    Unlike Google, NumPy makes no syntactic distinction between Raises entries
    and parameter entries -- every entry has the same 'name : type' header shape
    (or a bare type with no name, for unnamed Returns/Yields entries), so every
    entry is parsed by the same rule regardless of section keyword.
    """

    def _parse_parameter_item(
        self, header: str, description: str
    ) -> StructuredListParameter:
        """Parses a single (header, description) pair into a
        StructuredListParameter.

        Splits the header on the first ':' to separate name from type. If the
        header contains no ':' -- as is conventional for unnamed Returns/Yields
        entries, which document only the type -- the entire header is treated as
        the type, and the name is left as None.

        Args:
            header (str): The item's header line, e.g. 'x : int' or 'bool'.
            description (str): The item's description, already joined from any
                continuation lines.

        Returns:
            parameter (StructuredListParameter): The parsed parameter entry.
        """
        if STRUCTURED_LIST_DESCRIPTION_SEPARATOR in header:
            # Reused across styles: here it separates name from type on the
            # header line, not name/type from description as in Google.
            colon_index = header.index(STRUCTURED_LIST_DESCRIPTION_SEPARATOR)
            name = header[:colon_index].strip()
            variable_type = header[colon_index + 1 :].strip()
        else:
            name = None
            variable_type = header.strip()

        parameter = StructuredListParameter(
            name=name,
            type=variable_type,
            description=description,
        )

        return parameter

    def parse(self, content: str) -> StructuredList:
        """Parses raw NumPy-style structured-list section content into a
        StructuredList node.

        Args:
            content (str): The raw text of a structured-list section, including
                its keyword header line but with the dashed underline already
                removed by the scanner.

        Returns:
            structured_list (StructuredList): Fully parsed structured list node.
        """
        keyword = content.splitlines()[0].strip()
        items = extract_structured_items(content, skip_first_line=True)

        entries = [
            self._parse_parameter_item(header, description)
            for header, description in items
        ]

        structured_list = StructuredList(
            keyword=keyword,
            entries=entries,
        )

        return structured_list
