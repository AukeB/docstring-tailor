"""CLI configuration constants and allowed values for docstring_tailor."""

from enum import Enum
from typing import TypedDict

# Initial argument that specifies the file(s) and/or folder(s)
DEFAULT_PATHS = [("src")]


# Argument: '--style'
class DocstringStyle(str, Enum):
    """Supported docstring styles.

    Attributes:
        google (str): Google-style docstrings.
        numpy (str): NumPy-style docstrings.
        sphinx (str): Sphinx/reST-style docstrings.
        epydoc (str): Epydoc-style docstrings, not yet supported.
    """

    google = "google"
    numpy = "numpy"
    sphinx = "sphinx"
    epydoc = "epydoc"


SUPPORTED_STYLES = {DocstringStyle.google, DocstringStyle.numpy, DocstringStyle.sphinx}

# Argument: '--line-length'
LINE_LENGTH_MIN: int = 30
LINE_LENGTH_MAX: int = 300
LINE_LENGTH_DEFAULT: int = 100

# Settings read from the docstring_tailor section of pyproject.toml or
# docstring_tailor.toml. The keys are hyphenated as written in the config file,
# which a class body cannot express, so this uses the functional TypedDict form.
FileConfig = TypedDict(
    "FileConfig",
    {"line-length": int, "style": str, "exclude": list[str]},
    total=False,
)
