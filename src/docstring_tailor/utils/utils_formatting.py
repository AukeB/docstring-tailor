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


def _is_unordered_list(lines: list[str]) -> bool:
    """Returns True if at least two consecutive list items starting with an unordered marker are
    found, ignoring continuation lines from wrapped items.

    Args:
        lines (list[str]): The lines to check.

    Returns:
        result (bool): True if an unordered list is detected, False otherwise.
    """
    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        return False

    base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
    pattern = re.compile(r"^\s*[-*+]\s+")
    count = 0

    for line in lines:
        if not line.strip():
            continue

        if len(line) - len(line.lstrip()) == base_indent:
            if pattern.match(line):
                count += 1
                if count >= 2:
                    return True
            else:
                count = 0

    return False


def _is_ordered_list(lines: list[str]) -> bool:
    """Returns True if at least two consecutive sequentially numbered list items are found, ignoring
    continuation lines from wrapped items.

    Args:
        lines (list[str]): The lines to check.

    Returns:
        result (bool): True if an ordered list is detected, False otherwise.
    """
    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        return False

    base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
    pattern = re.compile(r"^\s*(\d+)[.)]\s+")
    expected = 1
    count = 0

    for line in lines:
        if not line.strip():
            continue

        if len(line) - len(line.lstrip()) == base_indent:
            match = pattern.match(line)
            if match and int(match.group(1)) == expected:
                count += 1
                expected += 1
                if count >= 2:
                    return True
            else:
                expected = 1
                count = 0

    return False


def is_list(text: str) -> bool:
    """Returns True if the text block contains an unordered or ordered list.

    Args:
        text (str): The text block to check.

    Returns:
        result (bool): True if a list is detected, False otherwise.
    """
    lines = text.split("\n")
    result = _is_unordered_list(lines=lines) or _is_ordered_list(lines=lines)

    return result


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
