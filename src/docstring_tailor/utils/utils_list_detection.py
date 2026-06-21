"""Utility module with functions for list detection in docstrings."""

from docstring_tailor.constants import (
    RE_PATTERN_ORDERED_LIST_ITEM,
    RE_PATTERN_UNORDERED_LIST_ITEM,
)


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
    count = 0

    for line in lines:
        if not line.strip():
            continue

        if len(line) - len(line.lstrip()) == base_indent:
            if RE_PATTERN_UNORDERED_LIST_ITEM.match(line):
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
    expected = 1
    count = 0

    for line in lines:
        if not line.strip():
            continue

        if len(line) - len(line.lstrip()) == base_indent:
            match = RE_PATTERN_ORDERED_LIST_ITEM.match(line)
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
