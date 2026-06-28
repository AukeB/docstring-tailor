"""CLI configuration constants and allowed values for docstring_tailor."""

from enum import Enum

# Initial argument that specifies the file(s) and/or folder(s)
DEFAULT_PATHS = [("src")]


# Argument: '--style'
class DocstringStyle(str, Enum):
    """Supported docstring styles."""

    google = "google"
    numpy = "numpy"
    sphinx = "sphinx"
    epydoc = "epydoc"


SUPPORTED_STYLES = {DocstringStyle.google}
DEFAULT_STYLE = DocstringStyle.google

# Argument: '--line-length'
LINE_LENGTH_MIN: int = 30
LINE_LENGTH_MAX: int = 300
LINE_LENGTH_DEFAULT: int = 100
