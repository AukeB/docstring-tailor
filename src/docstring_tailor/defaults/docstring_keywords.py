"""Defines keyword and directive sets for all supported docstring styles."""

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
