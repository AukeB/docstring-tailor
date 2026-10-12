"""Demonstrates a NumPy-style function docstring with
multiple sections.

This function exists purely as a formatting example and
illustrates how Parameters, Returns, Examples, and Raises
sections are structured in a NumPy-style docstring.

Parameters
----------
example_argument_1 : str
    First example input value used to construct a formatted
    result string.
example_argument_2 : int
    Second example input value used to influence the
    transformation logic.

Returns
-------
str
    A formatted string combining both input arguments into a
    single human-readable representation.

Yields
------
int
    The next value of the sequence.

Raises
------
ValueError
    Raised when example_argument_2 is negative or zero, as
    only positive integers are considered valid in this
    demonstration.

See Also
--------
compute_fast : The same computation with less memory.

Notes
-----
Keep this short.

Examples
--------
Basic usage:

>>> example_function("alpha", 3)
'alpha-3'
"""
