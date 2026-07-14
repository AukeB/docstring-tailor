def generate_windowed_stats(
    data: list[float],
    window_size: int,
    step: int = 1,
    min_value: float | None = None,
    max_value: float | None = None,
    precision: int = 2,
):
    """Generate rolling window statistics over a sequence of numerical data.

    Slides a fixed-size window across the input data, yielding summary
    statistics for each window position. Windows whose mean falls outside the
    optional value bounds are skipped entirely. This is useful for analysing
    trends in time series data without loading all results into memory at once.

    Processing steps:
    1. Validate the input arguments.
    2. Slide a fixed-size window over the input sequence.
    3. Compute the mean and standard deviation for each window.
    4. Skip windows whose mean falls outside the configured bounds.
    5. Yield the remaining statistics.

    Args:
        data (list[float]): The input sequence of numerical values to process.
        window_size (int): The number of elements in each window. Must be
            greater than zero and no larger than the length of data.
        step (int): The number of elements to advance the window between each
            yield. Defaults to 1.
        min_value (float | None): If provided, windows whose mean falls below
            this value are skipped. Defaults to None.
        max_value (float | None): If provided, windows whose mean exceeds this
            value are skipped. Defaults to None.
        precision (int): The number of decimal places to round yielded
            statistics to. Defaults to 2.

    Raises:
        ValueError: If window_size is less than 1.
        ValueError: If step is less than 1.
        ValueError: If window_size is greater than the length of data.

    Yields:
        index (int): The zero-based index of the window's starting position in
            data.
        mean (float): The arithmetic mean of the values in the current window,
            rounded to precision decimal places.
        std_dev (float): The standard deviation of the values in the current
            window, rounded to precision decimal places.

    Note:
        The algorithm in this function can be described in the following way:

        ```
        validate inputs
        
        for each sliding window:
            compute mean
            compute standard deviation
        
            if mean outside configured bounds:
                continue
        
            yield index, mean, standard deviation
        ```

    Examples:
        Basic usage over a short sequence.

        >>> data = [1.0, 2.0, 3.0, 4.0, 5.0]
        >>> for index, mean, std_dev in generate_windowed_stats(
        ...     data,
        ...     window_size=3,
        ... ):
        ...     print(index, mean, std_dev)
        0 2.0 0.82
        1 3.0 0.82
        2 4.0 0.82

        Windows can be filtered using lower and upper mean bounds.

        >>> for index, mean, std_dev in generate_windowed_stats(
        ...     data,
        ...     window_size=3,
        ...     min_value=2.5,
        ...     max_value=3.5,
        ... ):
        ...     print(index, mean, std_dev)
        1 3.0 0.82
    """
    if window_size < 1:
        raise ValueError("window_size must be at least 1")

    if step < 1:
        raise ValueError("step must be at least 1")

    if window_size > len(data):
        raise ValueError("window_size cannot exceed the length of data")

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