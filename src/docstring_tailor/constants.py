"""Module for storing project constants."""

import re
from collections import namedtuple
from pathlib import Path

# Repository relative file paths.
DIR_PATH_TEST_FIXTURES = Path(__file__).parent.parent.parent / "tests" / "fixtures"

# Encoding for reading .py files.
ENCODING: str = "utf-8"

# Docstring delimiter.
DOCSTRING_DELIMITER: str = '"""'
DOCSTRING_DELIMITER_LENGTH: int = len(DOCSTRING_DELIMITER)

# Google-style docstring section keywords for parsing (new logic).
GOOOGLE_NAMED_PARAGRAPH_SECTIONS = frozenset(
    {
        "Note",
        "Notes",
        "References",
        "See Also",
        "Warning",
        "Warnings",
    }
)
GOOOGLE_RAISES_SECTIONS = frozenset({"Raises"})
GOOOGLE_PARAMETER_SECTIONS = frozenset(
    {"Args", "Arguments", "Attributes", "Returns", "Yields"}
)
GOOOGLE_STRUCTURED_LIST_SECTIONS = GOOOGLE_RAISES_SECTIONS | GOOOGLE_PARAMETER_SECTIONS

# Google-style docstring section keywords for formatting (will be deprecated).
GOOGLE_PLAIN_SECTIONS = frozenset(
    {
        "Note",
        "Notes",
        "References",
        "See Also",
        "Warning",
        "Warnings",
    }
)
GOOGLE_ITEM_SECTIONS = frozenset(
    {"Args", "Arguments", "Attributes", "Raises", "Returns", "Yields"}
)
GOOGLE_CODE_SECTIONS = frozenset({"Example", "Examples"})
GOOGLE_SECTION_HEADERS = (
    GOOGLE_PLAIN_SECTIONS | GOOGLE_ITEM_SECTIONS | GOOGLE_CODE_SECTIONS
)

# NumPy-style docstring section keywords.
NUMPY_ITEM_SECTIONS = frozenset(
    {"Attributes", "Methods", "Parameters", "Raises", "Receives", "Returns", "Yields"}
)
NUMPY_PLAIN_SECTIONS = frozenset({"Examples", "Notes", "References", "See Also"})
NUMPY_SECTION_HEADERS = NUMPY_ITEM_SECTIONS | NUMPY_PLAIN_SECTIONS

# Sphinx/reST-style docstring directive markers.
# Directive-based rather than section-based — no section headers in the Google/NumPy sense.
SPHINX_ITEM_DIRECTIVES = frozenset({":param", ":raises", ":returns", ":rtype", ":type"})
SPHINX_PLAIN_DIRECTIVES = frozenset(
    {".. example::", ".. note::", ".. seealso::", ".. warning::"}
)
SPHINX_DIRECTIVES = SPHINX_ITEM_DIRECTIVES | SPHINX_PLAIN_DIRECTIVES

# Epydoc-style docstring tag markers.
# Tag-based rather than section-based — no section headers in the Google/NumPy sense.
EPYDOC_ITEM_TAGS = frozenset({"@param", "@raise", "@return", "@rtype", "@type"})
EPYDOC_PLAIN_TAGS = frozenset({"@note", "@warning"})
EPYDOC_TAGS = EPYDOC_ITEM_TAGS | EPYDOC_PLAIN_TAGS

# Python interactive/REPL prompt (Used in 'Example(s)' section).
PYTHON_REPL_PREFIX_START = ">>>"
PYTHON_REPL_PREFIX_CONTINUATION = "..."

# Fenced code block markers.
FENCED_CODE_BLOCK_BACKTICKS = "```"
FENCED_CODE_BLOCK_TILDES = "~~~"

CODE_BLOCK_PREFIXES = (
    PYTHON_REPL_PREFIX_START,
    FENCED_CODE_BLOCK_BACKTICKS,
    FENCED_CODE_BLOCK_TILDES,
)

# Named tuples
Section = namedtuple("Section", ["name", "body"])

# Regular expression patterns
RE_PATTERN_FENCE = re.compile(r"^\s*(```|~~~)", re.MULTILINE)
RE_PATTERN_BLANK_LINES = re.compile(r"\n\s*\n")
RE_PATTERN_UNORDERED_LIST_ITEM = re.compile(r"^\s*[-*+]\s+")
RE_PATTERN_ORDERED_LIST_ITEM = re.compile(r"^\s*(\d+)[.)]\s+")
