"""Module for shared paragraph formatting utility functions."""

import re
import textwrap


def wrap_paragraph(
    text: str,
    wrap_width: int,
    line_separator: str,
    subsequent_indent: str = "",
) -> str:
    """Normalises whitespace and wraps text to a given width.

    Strips leading and trailing whitespace, collapses all internal whitespace sequences to a single
    space, wraps to wrap_width, and joins the resulting lines with line_separator.

    Args:
        text (str): The raw text to wrap.
        wrap_width (int): Maximum number of characters per line.
        line_separator (str): The string used to join wrapped lines.
        subsequent_indent (str): String prepended to all lines except the first. Defaults to ''.

    Returns:
        formatted (str): The wrapped and joined paragraph string.
    """
    normalized = re.sub(r"\s+", " ", text.strip())
    lines = textwrap.wrap(
        normalized, width=wrap_width, subsequent_indent=subsequent_indent
    )
    formatted = line_separator.join(lines)

    return formatted
