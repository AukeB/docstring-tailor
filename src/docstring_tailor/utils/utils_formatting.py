"""Module for shared paragraph formatting utility functions."""

import re
import textwrap


def format_paragraph(
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


def format_list(text: str, wrap_width: int, line_separator: str) -> str:
    """Formats a list block, preserving each item on its own line.

    Groups lines into individual items by detecting list markers at the base indentation level.
    Continuation lines at a deeper indentation are joined to the current item. Each item is then
    wrapped independently, with continuation lines aligned to the text following the marker.

    Args:
        text (str): The raw list text.
        wrap_width (int): Maximum number of characters per line.
        line_separator (str): The string used to join lines and items.

    Returns:
        formatted (str): The formatted list string.
    """
    lines = [line for line in text.split("\n") if line.strip()]

    if not lines:
        return ""

    base_indent = min(len(line) - len(line.lstrip()) for line in lines)
    item_start_pattern = re.compile(r"^\s*(?:[-*+]|\d+[.)]) ")

    items: list[str] = []
    current_item_lines: list[str] = []

    for line in lines:
        indent = len(line) - len(line.lstrip())
        is_new_item = indent == base_indent and bool(item_start_pattern.match(line))

        if is_new_item and current_item_lines:
            items.append(" ".join(l.strip() for l in current_item_lines))
            current_item_lines = [line.strip()]
        else:
            current_item_lines.append(line.strip())

    if current_item_lines:
        items.append(" ".join(l.strip() for l in current_item_lines))

    formatted_items: list[str] = []
    for item in items:
        marker_match = re.match(r"^([-*+]\s+|\d+[.)]\s+)", item)
        subsequent_indent = " " * len(marker_match.group(1)) if marker_match else ""
        wrapped_lines = textwrap.wrap(
            item, width=wrap_width, subsequent_indent=subsequent_indent
        )
        formatted_items.append(line_separator.join(wrapped_lines))

    formatted = line_separator.join(formatted_items)

    return formatted
