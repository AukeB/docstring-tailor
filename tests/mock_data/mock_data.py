"""Mock data for DocstringVisitor tests."""

# Module docstrings.
# Formatting for the following scenarios:
# - Docstring is too long
# - Docstring text does not start on the same line as the triple quotes.


MODULE_DOCSTRING_TOO_LONG_INPUT = '''\
"""Module for doing something very important that has a really long description that exceeds the line length limit."""
'''

MODULE_DOCSTRING_TOO_LONG_EXPECTED = '''\
"""Module for doing something very important that has a really long description that exceeds the
line length limit.
"""
'''

MODULE_DOCSTRING_NOT_SAME_LINE_INPUT = '''\
"""
Module for doing something very important.
"""
'''

MODULE_DOCSTRING_NOT_SAME_LINE_EXPECTED = '''\
"""Module for doing something very important."""
'''