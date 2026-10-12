"""Computes the windowed statistic.

:param data: The input values    to  process, in order.
:type data:  list[float]
:param int window:   The size of each window
    in elements.
:param  step: How far the window moves each time.
:type step: int
:returns: The statistic for each window,
    one value per position.
:rtype: list[float]
:raises ValueError: If the window is larger than the data
    or not positive.
:raise TypeError:   If the data is not a list.
"""
