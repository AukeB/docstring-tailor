"""Contains the intermediate representation model for parsed docstrings."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal

SimpleListType = Literal["ordered", "unordered"]


class SectionType(Enum):
    """Enumerates all possible section types in a parsed docstring IR."""

    UNIDENTIFIED = auto()
    PARAGRAPH = auto()
    NAMED_PARAGRAPH = auto()
    CODE_BLOCK = auto()
    CODE_REPL = auto()
    STRUCTURED_LIST = auto()
    SIMPLE_LIST = auto()


@dataclass
class DocstringNode:
    """Base class for all docstring IR nodes.

    Attributes:
        section_type (SectionType): The classified type of this node.
    """

    section_type: SectionType


@dataclass
class DocstringSection(DocstringNode):
    """Represents a single typed chunk of raw text in the docstring IR.

    Attributes:
        section_type (SectionType): The classified type of this node.
        content (str): The raw text content of this section.
    """

    content: str


@dataclass
class StructuredListParameter:
    """Represents a single parsed parameter entry in a structured list section.

    Attributes:
        name (str): The variable or attribute name.
        type (str): The annotated type of the variable.
        description (str): The description of the variable.
    """

    name: str
    type: str
    description: str


@dataclass
class StructuredListError:
    """Represents a single parsed error entry in a Raises structured list section.

    Attributes:
        error_type (str): The exception type being raised.
        description (str): The description of when the error is raised.
    """

    error_type: str
    description: str


@dataclass
class ParsedStructuredList(DocstringNode):
    """Represents a fully parsed structured list section in the docstring IR.

    Attributes:
        keyword (str): The section keyword, e.g. 'Args', 'Returns', 'Raises'.
        entries (list[StructuredListParameter] | list[StructuredListError]):
            The parsed entries, typed according to the section keyword.
    """

    keyword: str
    entries: list[StructuredListParameter] | list[StructuredListError]


@dataclass
class ParsedSimpleList(DocstringNode):
    """Represents a fully parsed simple list section in the docstring IR.

    Attributes:
        section_type (SectionType): Always SectionType.SIMPLE_LIST.
        list_type (SimpleListType): Variable that stores whether the simple list is an
            ordered or unordered list.
        items (list[str]): The parsed list items as plain strings.
    """

    list_type: SimpleListType
    items: list[str]


@dataclass
class ParsedNamedParagraph(DocstringNode):
    """Represents a fully parsed named paragraph section in the docstring IR.

    Attributes:
        section_type (SectionType): Always SectionType.NAMED_PARAGRAPH.
        header (str): The section keyword, e.g. 'Note', 'Warning'.
        body (list[DocstringNode]): Parsed sub-sections of the body content.
    """

    header: str
    body: list[DocstringSection | ParsedSimpleList]
