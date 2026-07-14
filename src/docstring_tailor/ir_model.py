"""Intermediate representation (IR) model for parsed docstrings.

- Section types:
- Paragraph: A block of plain prose used for general descriptions or explanatory
  text.
- CodeBlock: A fenced block containing source code or other preformatted text.
- CodeREPL: An interactive interpreter session containing prompts and output.
- StructuredList: A semantic list with typed entries used for API documentation
  such as Args, Returns, Attributes, or Raises.
- SimpleList: An ordered or unordered list of plain text items used for general
  enumerations.
- NamedParagraph: A titled section containing nested Paragraph, CodeBlock,
  CodeREPL, and SimpleList sections, but not other NamedParagraph or
  StructuredList sections to prevent unlimited recursion and to remain
  consistent with PEP 257.
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
        code (str): The raw code content between the fence delimiters.
        delimiter (CodeBlockDelimiterType): The fence delimiter used to open and
            close the code block.
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
        name (str | None): The variable or attribute name, or None when the
            entry has no name -- the conventional shape for Returns and Yields
            entries, which document only the type.
        type (str): The annotated type of the variable.
        description (str): The description of the variable.
    """

    name: str | None
    type: str
    description: str


@dataclass
class StructuredListError:
    """Represents a single parsed error entry in a Raises structured list
    section.

    Attributes:
        error_type (str): The exception type being raised.
        description (str): The description of when the error is raised.
    """

    error_type: str
    description: str


@dataclass
class StructuredList(DocstringNode):
    """Represents a fully parsed structured list section in the docstring IR.

    Attributes:
        keyword (str): The section keyword, e.g. 'Args', 'Returns', 'Raises'.
        entries (list[StructuredListParameter] | list[StructuredListError]): The
            parsed entries, typed according to the section keyword.
    """

    keyword: str
    entries: list[StructuredListParameter] | list[StructuredListError]


@dataclass
class SimpleList(DocstringNode):
    """Represents a fully parsed simple list section in the docstring IR.

    Attributes:
        list_type (SimpleListType): Variable that stores whether the simple list
            is an ordered or unordered list.
        items (list[str]): The parsed list items as plain strings.
        has_leading_blank_line (bool): Whether the list was preceded by a blank
            line in the source. False only when the list immediately follows a
            Paragraph with no blank line between them; a SimpleList is always
            followed by a blank line, so this asymmetry is the only adjacency
            that needs tracking.
    """

    list_type: SimpleListType
    items: list[str]
    has_leading_blank_line: bool


@dataclass
class NamedParagraph(DocstringNode):
    """Represents a fully parsed named paragraph section in the docstring IR.

    Attributes:
        header (str): The section keyword, e.g. 'Note', 'Warning'.
        body (list[DocstringNode]): Parsed sub-sections of the body content.
    """

    header: str
    body: list[DocstringNode]
