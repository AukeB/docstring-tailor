"""Module for storing project constants."""

import re
from pathlib import Path

# Repository relative file paths.
DIR_PATH_TEST_FIXTURES = Path(__file__).parent.parent.parent / "tests" / "fixtures"

# Encoding for reading .py files.
ENCODING: str = "utf-8"

# All regular expression patterns used in the codebase are stored here.
RE_PATTERN_WHITESPACE = re.compile(r"\s+")
RE_PATTERN_BLANK_LINES = re.compile(r"\n\s*\n")
RE_PATTERN_CODE_BLOCK_DELIMITER = re.compile(r"^\s*(```|~~~)", re.MULTILINE)
RE_PATTERN_UNORDERED_LIST_ITEM = re.compile(r"^\s*[-*+]\s+")
RE_PATTERN_ORDERED_LIST_ITEM = re.compile(r"^\s*(\d+)[.)]\s+")
RE_PATTERN_SIMPLE_LIST_MARKER = re.compile(r"^[-*+]\s+|^\d+[.)]\s+")
RE_PATTERN_STRUCTURED_LIST_NAME_AND_TYPE = re.compile(
    r"^(?P<name>\S+)\s\((?P<type>.*)\)$"
)

# =========================================
# Constants used for all docstring formats.
# =========================================


# Docstring delimiter.
DOCSTRING_DELIMITER: str = '"""'
DOCSTRING_DELIMITER_LENGTH: int = len(DOCSTRING_DELIMITER)

# Character used after keyword/headings:
DOCSTRING_KEYWORD_SEPARATOR: str = ":"

# Related to CodeBlock sections.
CODE_BLOCK_DELIMITER_BACKTICKS: str = "```"
CODE_BLOCK_DELIMITER_TILDES: str = "~~~"

# Related to CodeREPL sections.
CODE_REPL_PROMPT: str = ">>>"
CODE_REPL_CONTINUATION_PROMPT: str = "..."

# Related to both CodeBlock and CodeREPL sections.
CODE_START_MARKERS = (
    CODE_REPL_PROMPT,
    CODE_BLOCK_DELIMITER_BACKTICKS,
    CODE_BLOCK_DELIMITER_TILDES,
)

# Related to SimpleList sections.
UNORDERED_LIST_MARKER: str = "- "
ORDERED_LIST_SEPARATOR = ". "


# ====================================================
# Constants used for multiple docstings (but not all).
# ====================================================


# Related to StructuredList sections (Use in Google and Numpy format)
STRUCTURED_LIST_DESCRIPTION_SEPARATOR: str = ":"
PARAMETER_TYPE_ANNOTATION_OPEN: str = "("
PARAMETER_TYPE_ANNOTATION_CLOSE: str = ")"


# ============================================
# Constants used for single docstring formats.
# ============================================


# Google
GOOGLE_NAMED_PARAGRAPH_SECTIONS = frozenset(
    {
        "Note",
        "Notes",
        "References",
        "See Also",
        "Warning",
        "Warnings",
        "Example",
        "Examples",
    }
)
GOOGLE_RAISES_SECTIONS = frozenset({"Raises"})
GOOGLE_PARAMETER_SECTIONS = frozenset(
    {"Args", "Arguments", "Attributes", "Returns", "Yields"}
)
GOOGLE_STRUCTURED_LIST_SECTIONS = GOOGLE_RAISES_SECTIONS | GOOGLE_PARAMETER_SECTIONS
GOOGLE_ALL_SECTION_KEYWORDS = (
    GOOGLE_NAMED_PARAGRAPH_SECTIONS | GOOGLE_STRUCTURED_LIST_SECTIONS
)


# NumPy
NUMPY_ITEM_SECTIONS = frozenset(
    {"Attributes", "Methods", "Parameters", "Raises", "Receives", "Returns", "Yields"}
)
NUMPY_PLAIN_SECTIONS = frozenset({"Examples", "Notes", "References", "See Also"})
NUMPY_SECTION_HEADERS = NUMPY_ITEM_SECTIONS | NUMPY_PLAIN_SECTIONS


# Sphinx/reST-style
SPHINX_ITEM_DIRECTIVES = frozenset({":param", ":raises", ":returns", ":rtype", ":type"})
SPHINX_PLAIN_DIRECTIVES = frozenset(
    {".. example::", ".. note::", ".. seealso::", ".. warning::"}
)
SPHINX_DIRECTIVES = SPHINX_ITEM_DIRECTIVES | SPHINX_PLAIN_DIRECTIVES


# Epydoc-style docstring tag markers.
EPYDOC_ITEM_TAGS = frozenset({"@param", "@raise", "@return", "@rtype", "@type"})
EPYDOC_PLAIN_TAGS = frozenset({"@note", "@warning"})
EPYDOC_TAGS = EPYDOC_ITEM_TAGS | EPYDOC_PLAIN_TAGS
