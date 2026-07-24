"""Demonstrates a minimal Google-style module docstring.

This module exists as a formatting example and illustrates the typical
structure of a Google-style docstring, including a concise summary
line followed by an additional descriptive paragraph.
"""


class ExampleConfiguration:
    """Represents a configuration object used to demonstrate Google-
    style class docstrings.

    This class is provided as a formatting example and illustrates how
    attributes are documented consistently in the Google docstring
    style.

    Attributes:
        example_argument_1 (str): Stores the first configuration value
            provided at initialization.
        example_argument_2 (int): Stores the second configuration
            value provided at initialization.
    """


def example_function(example_argument_1: str, example_argument_2: int) -> str:
    """Demonstrates a Google-style function docstring with multiple
    sections.

    This function exists purely as a formatting example and
    illustrates how Args, Returns, Examples, and Raises sections are
    structured in a Google-style docstring.

    Args:
        example_argument_1 (str): First example input value used to
            construct a formatted result string.
        example_argument_2 (int): Second example input value used to
            influence the transformation logic.

    Returns:
        str: A formatted string combining both input arguments into a
            single human-readable representation.

    Examples:
        Basic usage with typical inputs produces a simple combined
        string:

        >>> example_function("alpha", 3)
        'alpha-3'

        You can also write text in between two Python REPL sections,
        and this part will be formatted, while the two small code
        sections won't be formatted.

        >>> example_function(
        ...     "beta",
        ...     7,
        ... )
        'beta-7'

    Raises:
        ValueError: Raised when example_argument_2 is negative or
            zero, as only positive integers are considered valid in
            this demonstration.
    """
    if example_argument_2 <= 0:
        raise ValueError("example_argument_2 must be positive")

    return f"{example_argument_1}-{example_argument_2}"


"""Demonstrates that Google-style docstrings can include structured
lists.

This module-level docstring is used as a formatting example and shows
how numbered lists can be represented inside a docstring. Each list
item is recognized by the formatter and rendered on a separate line.

Steps:
1. Demonstrates that docstrings may contain structured numbered lists
   that are parsed and formatted consistently by the docstring
   formatter.
2. Shows that each list item is treated as a separate logical element
   and is wrapped independently when exceeding the configured line
   length.
3. Illustrates that long list items may span multiple lines while
   preserving indentation and list structure integrity across
   formatting operations.
"""

"""Demonstrates that Google-style docstrings can include structured
lists.

This module-level docstring is used as a formatting example and shows
how unordered lists can be represented inside a docstring. Each list
item is recognized by the formatter and rendered on a separate line.

Items:
- Demonstrates that docstrings may contain structured unordered lists
  that are parsed and formatted consistently by the docstring
  formatter.
- Shows that each list item is treated as an independent element and
  is wrapped separately when exceeding the configured line length.
- Illustrates that long list items may span multiple lines while
  preserving indentation and list structure integrity across
  formatting operations.
"""

#### Codeblocks

"""Demonstrates a Google-style module docstring containing a code
block.

This module-level docstring is used as a formatting example and shows
how code blocks can be embedded inside docstrings using fenced
delimiters.

Example:
    ```
    def example_function(x, y):
        return x + y
    ```
"""

"""Demonstrates a Google-style module docstring containing a code
block.

This module-level docstring is used as a formatting example and shows
how code blocks can be embedded inside docstrings using fenced
delimiters.

Example:
    ~~~
    def example_function(x, y):
        return x + y
    ~~~
"""

#### Other sections

def example_generator(n):
    """Generators have a ``Yields`` section instead of a ``Returns``
    section.

    Args:
        n (int): The upper limit of the range to generate, from 0 to
            `n` - 1.

    Yields:
        int: The next number in the range of 0 to `n` - 1.
    """


"""Demonstrates a Google-style module docstring containing a Note
section.

This module-level docstring is used as a formatting example and
illustrates how additional informational sections can be included
alongside the main description in a Google-style docstring.

Note:
    The formatting of this docstring is intentionally designed to test
    how note sections are detected and preserved during docstring
    transformation.
"""