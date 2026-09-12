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
RE_PATTERN_NUMPY_SECTION_UNDERLINE = re.compile(r"^-+$")


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


# ============================================
# Constants used for single docstring formats.
# ============================================


# === Google ===

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

GOOGLE_STRUCTURED_LIST_DESCRIPTION_SEPARATOR: str = ":"

# === NumPy ---

NUMPY_ITEM_SECTIONS = frozenset(
    {"Attributes", "Methods", "Parameters", "Raises", "Receives", "Returns", "Yields"}
)
NUMPY_PLAIN_SECTIONS = frozenset({"Examples", "Notes", "References", "See Also"})
NUMPY_SECTION_HEADERS = NUMPY_ITEM_SECTIONS | NUMPY_PLAIN_SECTIONS

NUMPY_STRUCTURED_LIST_NAME_TYPE_SEPARATOR: str = ":"

# Sphinx/reST-style
SPHINX_ITEM_DIRECTIVES = frozenset({":param", ":raises", ":returns", ":rtype", ":type"})
SPHINX_PLAIN_DIRECTIVES = frozenset(
    {".. example::", ".. note::", ".. seealso::", ".. warning::"}
)
SPHINX_DIRECTIVES = SPHINX_ITEM_DIRECTIVES | SPHINX_PLAIN_DIRECTIVES

# === Sphinx ===

# Sphinx field tags, grouped by the IR section they map to. Aliases (singular
# and plural spellings) are accepted on input; the renderer emits one canonical
# spelling per group. ':param' also accepts an inline type ':param <type>
# <name>:', handled by the parser.
SPHINX_PARAM_TAGS = frozenset({":param", ":parameter", ":arg", ":argument"})
SPHINX_TYPE_TAGS = frozenset({":type"})
SPHINX_RETURN_TAGS = frozenset({":return", ":returns"})
SPHINX_RTYPE_TAGS = frozenset({":rtype"})
SPHINX_RAISE_TAGS = frozenset({":raise", ":raises", ":except", ":exception"})

# All field tags that open a structured-list entry (as opposed to type metadata
# for a preceding entry). Used to detect the start of a field-list block.
SPHINX_FIELD_TAGS = (
    SPHINX_PARAM_TAGS
    | SPHINX_TYPE_TAGS
    | SPHINX_RETURN_TAGS
    | SPHINX_RTYPE_TAGS
    | SPHINX_RAISE_TAGS
)

# Canonical section keywords used for Sphinx StructuredList nodes in the IR, so
# keyword translation and rendering share one vocabulary.
SPHINX_KEYWORD_PARAMETERS: str = "Parameters"
SPHINX_KEYWORD_RETURNS: str = "Returns"
SPHINX_KEYWORD_RAISES: str = "Raises"

# Canonical Sphinx directive-to-header mapping for admonition sections rendered
# as NamedParagraph nodes.
SPHINX_DIRECTIVE_HEADERS: dict[str, str] = {
    ".. note::": "Note",
    ".. warning::": "Warning",
    ".. seealso::": "See Also",
    ".. example::": "Example",
}

# Reverse mapping: canonical header to its Sphinx directive marker, for
# rendering NamedParagraph nodes back to reST directives.
SPHINX_HEADER_DIRECTIVES: dict[str, str] = {
    header: directive for directive, header in SPHINX_DIRECTIVE_HEADERS.items()
}

# Canonical Sphinx field-tag spellings emitted my the renderer.
SPHINX_RENDER_PARAM_TAG: str = ":param"
SPHINX_RENDER_TYPE_TAG: str = ":type"
SPHINX_RENDER_RETURNS_TAG: str = ":returns"
SPHINX_RENDER_RTYPE_TAG: str = ":rtype"
SPHINX_RENDER_RAISES_TAG: str = ":raises"

# === Epydoc ===

EPYDOC_ITEM_TAGS = frozenset({"@param", "@raise", "@return", "@rtype", "@type"})
EPYDOC_PLAIN_TAGS = frozenset({"@note", "@warning"})
EPYDOC_TAGS = EPYDOC_ITEM_TAGS | EPYDOC_PLAIN_TAGS
