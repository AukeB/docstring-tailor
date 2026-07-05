"""Intermediate representation (IR) model for parsed docstrings.

Section types:
- Paragraph: A block of plain prose used for general descriptions or explanatory text.
- CodeBlock: A fenced block containing source code or other preformatted text.
- CodeREPL: An interactive interpreter session containing prompts and output.
- StructuredList: A semantic list with typed entries used for API documentation such as Args, Returns, Attributes, or Raises.
- SimpleList: An ordered or unordered list of plain text items used for general enumerations.
- NamedParagraph: A titled section containing nested Paragraph, CodeBlock, CodeREPL,
    and SimpleList sections, but not other NamedParagraph or StructuredList sections to prevent
    unlimited recursion and to remain consistent with PEP 257.
"""

from dataclasses import dataclass
from typing import Literal

SimpleListType = Literal["ordered", "unordered"]
CodeBlockDelimiterType = Literal["```", "~~~"]


class DocstringNode:
    """Base class for all docstring IR nodes."""


@dataclass
class Paragraph(DocstringNode):
    """Represents a single typed chunk of raw text in the docstring IR."""

    content: str


@dataclass
class CodeBlock(DocstringNode):
    """Represents a fenced code block section in the docstring IR.

    Attributes:
        code: The raw code content between the fence delimiters.
        delimiter: The fence delimiter used to open and close the code block.
    """

    code: str
    delimiter: CodeBlockDelimiterType


@dataclass
class CodeREPL(DocstringNode):
    """Represents an interactive REPL-style code section in the docstring IR."""

    code: str


@dataclass
class StructuredListParameter:
    """Represents a single parsed parameter entry in a structured list section.

    Attributes:
        name: The variable or attribute name.
        type: The annotated type of the variable.
        description: The description of the variable.
    """

    name: str
    type: str
    description: str


@dataclass
class StructuredListError:
    """Represents a single parsed error entry in a Raises structured list section.

    Attributes:
        error_type: The exception type being raised.
        description: The description of when the error is raised.
    """

    error_type: str
    description: str


@dataclass
class StructuredList(DocstringNode):
    """Represents a fully parsed structured list section in the docstring IR.

    Attributes:
        keyword: The section keyword, e.g. 'Args', 'Returns', 'Raises'.
        entries: The parsed entries, typed according to the section keyword.
    """

    keyword: str
    entries: list[StructuredListParameter] | list[StructuredListError]


@dataclass
class SimpleList(DocstringNode):
    """Represents a fully parsed simple list section in the docstring IR.

    Attributes:
        list_type: Variable that stores whether the simple list is an ordered or unordered list.
        items: The parsed list items as plain strings.
    """

    list_type: SimpleListType
    items: list[str]


@dataclass
class NamedParagraph(DocstringNode):
    """Represents a fully parsed named paragraph section in the docstring IR.

    Attributes:
        header: The section keyword, e.g. 'Note', 'Warning'.
        body: Parsed sub-sections of the body content.
    """

    header: str
    body: list[DocstringNode]
