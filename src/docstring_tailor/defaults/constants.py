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

# Regular expression patterns
RE_PATTERN_FENCE = re.compile(r"^\s*(```|~~~)", re.MULTILINE)
RE_PATTERN_BLANK_LINES = re.compile(r"\n\s*\n")
RE_PATTERN_UNORDERED_LIST_ITEM = re.compile(r"^\s*[-*+]\s+")
RE_PATTERN_ORDERED_LIST_ITEM = re.compile(r"^\s*(\d+)[.)]\s+")
RE_PATTERN_LIST_MARKER = re.compile(r"^[-*+]\s+|^\d+[.)]\s+")
