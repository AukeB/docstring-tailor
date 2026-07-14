"""Utility module with functions for list detection in docstrings."""

from docstring_tailor.constants import (
    RE_PATTERN_ORDERED_LIST_ITEM,
    RE_PATTERN_UNORDERED_LIST_ITEM,
)
from docstring_tailor.ir_model import SimpleListType


def _find_unordered_list_start(lines: list[str]) -> int | None:
    """Returns the index of the first line of the earliest confirmed unordered
    list run, ignoring continuation lines from wrapped items.

    A run is confirmed once two consecutive lines at the base indentation match
    the unordered marker pattern. The index returned is that of the first of
    those two lines, not the second, so a caller can split a preceding paragraph
    off cleanly.

    Args:
        lines (list[str]): The lines to check.

    Returns:
        start_index (int | None): The index of the first line of the earliest
            confirmed run, or None if no confirmed run exists.
    """
    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        return None

    base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
    count = 0
    candidate_index: int | None = None

    for index, line in enumerate(lines):
        if not line.strip():
            continue

        if len(line) - len(line.lstrip()) == base_indent:
            if RE_PATTERN_UNORDERED_LIST_ITEM.match(line):
                if count == 0:
                    candidate_index = index

                count += 1

                if count >= 2:
                    return candidate_index
            else:
                count = 0
                candidate_index = None

    return None


def _find_ordered_list_start(lines: list[str]) -> int | None:
    """Returns the index of the first line of the earliest confirmed ordered
    list run, ignoring continuation lines from wrapped items.

    A run is confirmed once two consecutive lines at the base indentation are
    sequentially numbered. The index returned is that of the first of those two
    lines, not the second, so a caller can split a preceding paragraph off
    cleanly.

    Args:
        lines (list[str]): The lines to check.

    Returns:
        start_index (int | None): The index of the first line of the earliest
            confirmed run, or None if no confirmed run exists.
    """
    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        return None

    base_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
    expected = 1
    count = 0
    candidate_index: int | None = None

    for index, line in enumerate(lines):
        if not line.strip():
            continue

        if len(line) - len(line.lstrip()) == base_indent:
            match = RE_PATTERN_ORDERED_LIST_ITEM.match(line)

            if match and int(match.group(1)) == expected:
                if count == 0:
                    candidate_index = index

                count += 1
                expected += 1

                if count >= 2:
                    return candidate_index
            else:
                expected = 1
                count = 0
                candidate_index = None

    return None


def _is_unordered_list(lines: list[str]) -> bool:
    """Returns True if at least two consecutive list items starting with an
    unordered marker are found, ignoring continuation lines from wrapped items.

    Args:
        lines (list[str]): The lines to check.

    Returns:
        result (bool): True if an unordered list is detected, False otherwise.
    """
    result = _find_unordered_list_start(lines) is not None

    return result


def _is_ordered_list(lines: list[str]) -> bool:
    """Returns True if at least two consecutive sequentially numbered list items
    are found, ignoring continuation lines from wrapped items.

    Args:
        lines (list[str]): The lines to check.

    Returns:
        result (bool): True if an ordered list is detected, False otherwise.
    """
    result = _find_ordered_list_start(lines) is not None

    return result


def find_list_start(text: str) -> int | None:
    """Returns the index of the line where a confirmed list run begins, if the
    text contains one.

    Assumes a SimpleList is always followed by a blank line by the time content
    reaches here, so a chunk can contain at most a leading paragraph followed by
    a single list run extending to the end of the chunk -- never a list resuming
    after trailing prose. Checks for both list types and returns the earliest
    confirmed start, in the rare case both produce a candidate.

    Args:
        text (str): The text block to check.

    Returns:
        list_start_index (int | None): The index of the first line of the
            confirmed list run, or None if no confirmed list exists.
    """
    lines = text.split("\n")
    unordered_start = _find_unordered_list_start(lines)
    ordered_start = _find_ordered_list_start(lines)
    candidates = [
        index for index in (unordered_start, ordered_start) if index is not None
    ]

    if not candidates:
        return None

    list_start_index = min(candidates)

    return list_start_index


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


def get_list_type(text: str) -> SimpleListType:
    """Returns whether a confirmed list is ordered or unordered.

    Assumes the text is already confirmed to contain a list. Checks for
    unordered markers first, falling back to ordered. Note that this function
    intentionally repeats the detection scan already performed by is_list,
    favouring single responsibility over avoiding redundant computation.

    Args:
        text (str): The raw list text.

    Returns:
        list_type (SimpleListType): 'unordered' or 'ordered'.
    """
    lines = text.split("\n")
    list_type: SimpleListType = "unordered" if _is_unordered_list(lines) else "ordered"

    return list_type
