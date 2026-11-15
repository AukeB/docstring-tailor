def example_function(example_argument_1: str, example_argument_2: int) -> str:
    """Demonstrates a function docstring with multiple sections.

    This function exists purely as a formatting example and illustrates how the
    argument, return value, example, and exception sections of a docstring are
    structured.

    Args:
        example_argument_1 (str): First example input value used to construct a
            formatted result string.
        example_argument_2 (int): Second example input value used to influence the
            transformation logic.

    Returns:
        str: A formatted string combining both input arguments into a single
            human-readable representation.

    Examples:
        Basic usage with typical inputs produces a simple combined string:

        >>> example_function("alpha", 3)
        'alpha-3'

    Raises:
        ValueError: Raised when example_argument_2 is negative or zero, as only
            positive integers are considered valid in this demonstration.
    """
    if example_argument_2 <= 0:
        raise ValueError("example_argument_2 must be positive")

    return f"{example_argument_1}-{example_argument_2}"
