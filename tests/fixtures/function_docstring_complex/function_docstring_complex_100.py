def generate_windowed_stats(
    data: list[float],
    window_size: int,
    step: int = 1,
    min_value: float | None = None,
    max_value: float | None = None,
    precision: int = 2,
):
    """Generates rolling window statistics over a sequence of numerical data.

    Slides a window of fixed size across the input data, yielding summary statistics for each window
    position. Windows whose mean falls outside the optional value bounds are skipped entirely. This
    is useful for analysing trends in time series data without loading all results into memory at
    once.

    Args:
        data (list[float]): The input sequence of numerical values to process.
        window_size (int): The number of elements in each window. Must be greater than zero and no
            larger than the length of data.
        step (int): The number of elements to advance the window between each yield. Defaults to 1.
        min_value (float | None): If provided, windows whose mean falls below this value are
            skipped. Defaults to None.
        max_value (float | None): If provided, windows whose mean exceeds this value are skipped.
            Defaults to None.
        precision (int): The number of decimal places to round yielded statistics to. Defaults to 2.

    Yields:
        index (int): The zero-based index of the window's starting position in data.
        mean (float): The arithmetic mean of the values in the current window, rounded to precision
            decimal places.
        std_dev (float): The standard deviation of the values in the current window, rounded to
            precision decimal places.

    Examples:
        Basic usage over a short sequence, stepping one position at a time. The loop body uses
        continuation lines to stay within the line length limit.

        >>> data = [1.0, 2.0, 3.0, 4.0, 5.0]
        >>> for index, mean, std_dev in generate_windowed_stats(data, window_size=3):
        ...     print(index, mean, std_dev)
        0 2.0 0.82
        1 3.0 0.82
        2 4.0 0.82

        Increasing the step size reduces the number of windows yielded. The multi-line call below
        uses ellipsis continuation to keep each argument on its own line, which is preferred when
        there are many keyword arguments.

        >>> results = list(generate_windowed_stats(
        ...     data,
        ...     window_size=3,
        ...     step=2,
        ...     precision=4,
        ... ))
        >>> for index, mean, std_dev in results:
        ...     print(index, mean, std_dev)
        0 2.0000 0.8165
        2 4.0000 0.8165

        Value bounds filter out windows whose mean falls outside the desired range. Only the middle
        window survives here since its mean of 3.0 is the only one within the bounds of 2.5 and 3.5.

        >>> for index, mean, std_dev in generate_windowed_stats(
        ...     data,
        ...     window_size=3,
        ...     min_value=2.5,
        ...     max_value=3.5,
        ... ):
        ...     print(index, mean, std_dev)
        1 3.0 0.82
    """
    for i in range(0, len(data) - window_size + 1, step):
        window = data[i : i + window_size]
        mean = round(sum(window) / window_size, precision)
        variance = sum((x - mean) ** 2 for x in window) / window_size
        std_dev = round(variance**0.5, precision)

        if min_value is not None and mean < min_value:
            continue
        if max_value is not None and mean > max_value:
            continue

        yield i, mean, std_dev
