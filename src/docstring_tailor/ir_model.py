"""Contains the intermediate representation model for parsed docstrings."""

from dataclasses import dataclass
from enum import Enum, auto


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
        section_type (SectionType): Always SectionType.STRUCTURED_LIST.
        entries (list[StructuredListParameter] | list[StructuredListError]):
            The parsed entries, typed according to the section keyword.
    """

    entries: list[StructuredListParameter] | list[StructuredListError]
