"""Module for storing project constants."""

# Encoding for reading .py files.
ENCODING: str = "utf-8"

# Docstring delimiters.
DOCSTRING_DELIMITER: str = '"""'
DOCSTRING_DELIMITER_LENGTH: int = len(DOCSTRING_DELIMITER)

# Google-style docstring section keywords.
GOOGLE_ITEM_SECTIONS = frozenset(
    {
        "Args",
        "Arguments",
        "Attributes",
        "Raises",
        "Returns",
        "Yields",
    }
)
GOOGLE_PLAIN_SECTIONS = frozenset(
    {
        "Example",
        "Examples",
        "Note",
        "Notes",
        "References",
        "See Also",
        "Todo",
        "Warning",
        "Warnings",
    }
)
GOOGLE_SECTION_HEADERS = GOOGLE_ITEM_SECTIONS | GOOGLE_PLAIN_SECTIONS

# NumPy-style docstring section keywords.
NUMPY_ITEM_SECTIONS = frozenset(
    {
        "Attributes",
        "Methods",
        "Other Parameters",
        "Parameters",
        "Raises",
        "Receives",
        "Returns",
        "Yields",
    }
)
NUMPY_PLAIN_SECTIONS = frozenset(
    {
        "Examples",
        "Notes",
        "References",
        "See Also",
    }
)
NUMPY_SECTION_HEADERS = NUMPY_ITEM_SECTIONS | NUMPY_PLAIN_SECTIONS

# Sphinx/reST-style docstring directive markers.
# Directive-based rather than section-based — no section headers in the Google/NumPy sense.
SPHINX_ITEM_DIRECTIVES = frozenset(
    {
        ":param",
        ":raises",
        ":returns",
        ":rtype",
        ":type",
    }
)
SPHINX_PLAIN_DIRECTIVES = frozenset(
    {
        ".. example::",
        ".. note::",
        ".. seealso::",
        ".. warning::",
    }
)
SPHINX_DIRECTIVES = SPHINX_ITEM_DIRECTIVES | SPHINX_PLAIN_DIRECTIVES

# Epydoc-style docstring tag markers.
# Tag-based rather than section-based — no section headers in the Google/NumPy sense.
EPYDOC_ITEM_TAGS = frozenset(
    {
        "@param",
        "@raise",
        "@return",
        "@rtype",
        "@type",
    }
)
EPYDOC_PLAIN_TAGS = frozenset(
    {
        "@note",
        "@warning",
    }
)
EPYDOC_TAGS = EPYDOC_ITEM_TAGS | EPYDOC_PLAIN_TAGS

# pydoc is a documentation viewer, not a docstring format.
# It has no distinct section keywords and renders whatever is in the docstring.
