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
class DocstringSection:
    """Represents a single typed chunk in a docstring IR.

    Attributes:
        section_type (SectionType): The classified type of this section.
        content (str): The raw text content of this section.
    """

    section_type: SectionType
    content: str
