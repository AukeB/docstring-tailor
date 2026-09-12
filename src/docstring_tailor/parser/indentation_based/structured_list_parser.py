"""Contains the abstract base class for structured list section parsers."""

from abc import ABC, abstractmethod

from docstring_tailor.constants import (
    DOCSTRING_KEYWORD_SEPARATOR,
    GOOGLE_RAISES_SECTIONS,
    GOOGLE_STRUCTURED_LIST_DESCRIPTION_SEPARATOR,
    NUMPY_STRUCTURED_LIST_NAME_TYPE_SEPARATOR,
    RE_PATTERN_STRUCTURED_LIST_NAME_AND_TYPE,
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

    Determines whether the section is a Raises section or a Parameter section
    based on the keyword on the first line, then parses each item accordingly.
    """

    def _parse_parameter_item(self, item: str) -> StructuredListParameter:
        """Parses a single parameter item string into a StructuredListParameter.

        When the item has no ':' separator at all, its type and description
        cannot be told apart, so the whole item is preserved in the description
        with name and type left as None. Otherwise the text before the first ':'
        is split off and matched against the "name (type)" shape: on a match
        both name and type are extracted; otherwise the name is left as None and
        that text becomes the type, covering both the conventional
        Returns/Yields "type: description" entry and a malformed parameter entry
        whose "name (type)" could not be recovered.

        Args:
            item (str): A single joined item string.

        Returns:
            parameter (StructuredListParameter): The parsed parameter entry.
        """
        if GOOGLE_STRUCTURED_LIST_DESCRIPTION_SEPARATOR not in item:
            parameter = StructuredListParameter(name=None, type=None, description=item)
            return parameter

        colon_index = item.index(GOOGLE_STRUCTURED_LIST_DESCRIPTION_SEPARATOR)
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
        When the item has no ':' the two cannot be told apart, so the whole item
        is preserved in the description with error_type left as None, consistent
        with how an unclassifiable parameter entry is handled.

        Args:
            item (str): A single joined item string.

        Returns:
            error (StructuredListError): The parsed error entry.
        """
        if GOOGLE_STRUCTURED_LIST_DESCRIPTION_SEPARATOR not in item:
            error = StructuredListError(error_type=None, description=item)
            return error

        colon_index = item.index(GOOGLE_STRUCTURED_LIST_DESCRIPTION_SEPARATOR)
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
        self,
        header: str,
        description: str,
    ) -> StructuredListParameter:
        """Parses a single (header, description) pair into a
        StructuredListParameter.

        Splits the header on the first ':' to separate name from type. When the
        header contains no ':', whether a conventional unnamed Returns/Yields
        entry documenting only the type, or a malformed parameter entry, the
        whole reader is treated as the type and the name is left as None. The
        description is always kept separate, so no content is lost even when the
        header cannot be split.

        Args:
            header (str): The item's header line, e.g. 'x : int' or 'bool'.
            description (str): The item's description, already joined from any
                continuation lines.

        Returns:
            parameter (StructuredListParameter): The parsed parameter entry.
        """
        if NUMPY_STRUCTURED_LIST_NAME_TYPE_SEPARATOR in header:
            colon_index = header.index(NUMPY_STRUCTURED_LIST_NAME_TYPE_SEPARATOR)
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
