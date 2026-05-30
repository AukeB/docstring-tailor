# Module for storing project constants.

from pathlib import Path

# Main constants/parameters for now.
FILE_PATH_INPUT: Path = Path("data/test_input.py")
FILE_PATH_OUTPUT: Path = Path("data/test_output.py")
ENCODING: str = "utf-8"


# Docstring related parameters.
DOCSTRING_DELIMITER: str = '"""'
DOCSTRING_DELIMITER_LENGTH: int = len(DOCSTRING_DELIMITER)

# Runtime parameters.
LINE_LENGTH: int = 100  # Maximum characters per line (defaults to `100`).
STYLE: str = "Google"  # Docstring format style. Options: ["Google"].
IN_PLACE: bool = (
    True  # Whether to write files back or just print the diff (defaults to 'True')
)
