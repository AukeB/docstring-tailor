"""Demonstrates a NumPy-style function docstring with multiple sections.

This function exists purely as a formatting example and illustrates how
Parameters, Returns, Examples, and Raises sections are structured in a NumPy-
style docstring.

:param example_argument_1: First example input value used to construct a
    formatted result string.
:type example_argument_1: str
:param example_argument_2: Second example input value used to influence the
    transformation logic.
:type example_argument_2: int
:returns A formatted string combining both input arguments into a single human-
    readable representation.
:rtype str
:returns The next value of the sequence.
:rtype int
:param ValueError: Raised when example_argument_2 is negative or zero, as only
    positive integers are considered valid in this demonstration.

.. seealso::
    compute_fast : The same computation with less memory.

.. note::
    Keep this short.

.. example::
    Basic usage:

    >>> example_function("alpha", 3)
    'alpha-3'
"""
