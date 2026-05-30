"""Module for storing project constants."""

# Encoding for reading .py files.
ENCODING: str = "utf-8"

# Docstring related parameters.
DOCSTRING_DELIMITER: str = '"""'
DOCSTRING_DELIMITER_LENGTH: int = len(DOCSTRING_DELIMITER)

# For now, focus on 'google' type docstrings only.
ITEM_SECTIONS = frozenset({"Args", "Attributes", "Raises", "Returns"})
PLAIN_SECTIONS = frozenset({"Example", "Note"})
SECTION_HEADERS = ITEM_SECTIONS | PLAIN_SECTIONS
