"""Module for storing project constants."""

import re
from pathlib import Path

# Repository relative file paths.
DIR_PATH_TEST_FIXTURES = (
    Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"
)

# Encoding for reading .py files.
ENCODING: str = "utf-8"

# Docstring delimiter.
DOCSTRING_DELIMITER: str = '"""'
DOCSTRING_DELIMITER_LENGTH: int = len(DOCSTRING_DELIMITER)

# Python interactive/REPL prompt (Used in 'Example(s)' section).
CODE_REPL_PROMPT: str = ">>>"
CODE_REPL_CONTINUATION_PROMPT: str = "..."

# Fenced code block markers.
CODE_BLOCK_DELIMITER_BACKTICKS: str = "```"
CODE_BLOCK_DELIMITER_TILDES: str = "~~~"

CODE_START_MARKERS = (
    CODE_REPL_PROMPT,
    CODE_BLOCK_DELIMITER_BACKTICKS,
    CODE_BLOCK_DELIMITER_TILDES,
)

STRUCTURED_LIST_DESCRIPTION_SEPARATOR: str = ":"
PARAMETER_TYPE_ANNOTATION_OPEN: str = "("
PARAMETER_TYPE_ANNOTATION_CLOSE: str = ")"


# Regular expression patterns
RE_PATTERN_CODE_BLOCK_DELIMITER = re.compile(r"^\s*(```|~~~)", re.MULTILINE)
RE_PATTERN_BLANK_LINES = re.compile(r"\n\s*\n")
RE_PATTERN_UNORDERED_LIST_ITEM = re.compile(r"^\s*[-*+]\s+")
RE_PATTERN_ORDERED_LIST_ITEM = re.compile(r"^\s*(\d+)[.)]\s+")
RE_PATTERN_LIST_MARKER = re.compile(r"^[-*+]\s+|^\d+[.)]\s+")
