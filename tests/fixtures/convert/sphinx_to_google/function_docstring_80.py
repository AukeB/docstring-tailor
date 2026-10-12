"""Demonstrates a Sphinx-style function docstring with multiple sections.

This function exists purely as a formatting example and illustrates how
parameters, return values, and raised exceptions are documented using
reStructuredText info fields.

Args:
    example_argument_1 (str): First example input value used to construct a
        formatted result string.
    example_argument_2 (int): Second example input value used to influence the
        transformation logic.

Returns:
    str: A formatted string combining both input arguments into a single human-
        readable representation.

Raises:
    ValueError: Raised when example_argument_2 is negative or zero, as only
        positive integers are considered valid in this demonstration.

Note:
    Additional informational directives such as ``.. note::`` and ``..
    warning::`` are recognized and preserved during formatting.

Example:
    >>> example_function("alpha", 3)
    'alpha-3'
"""
