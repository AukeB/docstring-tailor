"""Demonstrates a Sphinx-style function docstring with multiple sections.

This function exists purely as a formatting example and illustrates how
parameters, return values, and raised exceptions are documented using
reStructuredText info fields.

:param example_argument_1: First example input value used to construct a
    formatted result string.
:type example_argument_1: str
:param example_argument_2: Second example input value used to influence the
    transformation logic.
:type example_argument_2: int
:returns A formatted string combining both input arguments into a single human-
    readable representation.
:rtype str
:raises ValueError: Raised when example_argument_2 is negative or zero, as only
    positive integers are considered valid in this demonstration.

.. note::
    Additional informational directives such as ``.. note::`` and ``..
    warning::`` are recognized and preserved during formatting.

.. example::
    >>> example_function("alpha", 3)
    'alpha-3'
"""
