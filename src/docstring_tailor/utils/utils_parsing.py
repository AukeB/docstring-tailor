"""Utility functions for parsing docstring section content."""

import re

from docstring_tailor.constants import RE_PATTERN_SIMPLE_LIST_MARKER
from docstring_tailor.utils.utils_formatting import get_indent


def _join_item_lines(item_lines: list[str]) -> str:
    """Joins the raw lines of one item into a single flat string.

    The first line is stripped and the continuation lines are stripped and
    joined by a single space.

    Args:
        item_lines (list[str]): The raw lines belonging to one item, header
            first.

    Returns:
        item (str): The flattened item string.
    """

    first_line = item_lines[0].strip()
    continuation_lines = [line.strip() for line in item_lines[1:]]
    continuation = " ".join(continuation_lines)

    item = f"{first_line} {continuation}".strip()

    return item


def _build_structured_item(item_lines: list[str]) -> tuple[str, str]:
    """Builds a single (header, description) tuple from an item's raw lines.

    Args:
        item_lines (list[str]): The raw lines belonging to one item, header
            first.

    Returns:
        item (tuple[str, str]): The stripped, marker-free header, paired with
            its description built by joining continuation lines with a single
            space.
    """

    stripped_header = item_lines[0].strip()
    header = re.sub(RE_PATTERN_SIMPLE_LIST_MARKER, "", stripped_header)

    description_lines = [line.strip() for line in item_lines[1:]]
    description = " ".join(description_lines)

    item = (header, description)

    return item


def extract_items(content: str, skip_first_line: bool = False) -> list[str]:
    """Extracts individual item strings from a section, using indentation to
    detect boundaries.

    Lines at the base indentation level start a new item. Continuation lines at
    a deeper indentation are joined to the preceding item.

    Args:
        content (str): The raw section content.
        skip_first_line (bool): Whether to skip the first line, e.g. for
            sections with a keyword header like 'Args:'.

    Returns:
        items (list[str]): Each item as a single joined string.
    """

    lines = content.splitlines()

    if skip_first_line:
        lines = lines[1:]

    lines = [line for line in lines if line.strip()]

    if not lines:
        empty_items: list[str] = []

        return empty_items

    indents = [get_indent(line) for line in lines]
    base_indent = min(indents)

    items: list[str] = []
    current_item_lines: list[str] = []

    for line in lines:
        current_indent = get_indent(line)

        if current_indent == base_indent and current_item_lines:
            item = _join_item_lines(item_lines=current_item_lines)
            items.append(item)

            current_item_lines = [line]
        else:
            current_item_lines.append(line)

    item = _join_item_lines(item_lines=current_item_lines)
    items.append(item)

    items = [re.sub(RE_PATTERN_SIMPLE_LIST_MARKER, "", item) for item in items]

    return items


def extract_structured_items(
    content: str, skip_first_line: bool = False
) -> list[tuple[str, str]]:
    """Extracts (header, description) tuples from a section, using indentation
    to detect item boundaries.

    Uses the same boundary-detection rule as extract_items, but does not flatten
    a header line into its description. This matters for styles like NumPy,
    where the header line alone (e.g. 'x : int') carries information -- the type
    -- with no remaining delimiter to recover it once joined to the description
    by a space. extract_items is safe to flatten because Google's equivalent
    information (name, type, and description) all live on one logical line
    before any splitting happens; here, they don't.

    Args:
        content (str): The raw section content.
        skip_first_line (bool): Whether to skip the first line, e.g. for
            sections with a keyword header line.

    Returns:
        items (list[tuple[str, str]]): Each item as a (header, description)
            tuple, with continuation lines in the description joined by a single
            space.
    """

    lines = content.splitlines()

    if skip_first_line:
        lines = lines[1:]

    lines = [line for line in lines if line.strip()]

    if not lines:
        empty_items: list[tuple[str, str]] = []

        return empty_items

    indents = [get_indent(line) for line in lines]
    base_indent = min(indents)

    items: list[tuple[str, str]] = []
    current_item_lines: list[str] = []

    for line in lines:
        current_indent = get_indent(line)

        if current_indent == base_indent and current_item_lines:
            item = _build_structured_item(item_lines=current_item_lines)
            items.append(item)

            current_item_lines = [line]
        else:
            current_item_lines.append(line)

    item = _build_structured_item(item_lines=current_item_lines)
    items.append(item)

    return items
