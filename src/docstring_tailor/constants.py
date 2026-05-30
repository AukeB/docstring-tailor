# Module for storing project constants.

from pathlib import Path

# Related to data
DIRECTORY_PATH_INPUT: Path = Path("data/input/")
DIRECTORY_PATH_OUTPUT: Path = Path("data/output/")
ENCODING: str = "utf-8"

# Docstring related parameters.
DOCSTRING_DELIMITER: str = '"""'
DOCSTRING_DELIMITER_LENGTH: int = len(DOCSTRING_DELIMITER)

ITEM_SECTIONS = frozenset({"Args", "Attributes", "Raises", "Returns"})
PLAIN_SECTIONS = frozenset({"Example", "Note"})
SECTION_HEADERS = ITEM_SECTIONS | PLAIN_SECTIONS

# Runtime parameters.
LINE_LENGTH: int = 100  # Maximum characters per line (defaults to `100`).
STYLE: str = "Google"  # Docstring format style. Options: ["Google"].
