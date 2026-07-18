"""Utility functions for parsing docstring section content."""

import re

from docstring_tailor.constants import RE_PATTERN_SIMPLE_LIST_MARKER


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
    base_indent = min(len(line) - len(line.lstrip()) for line in lines)

    items: list[str] = []
    current_item_lines: list[str] = []

    for line in lines:
        current_indent = len(line) - len(line.lstrip())

        if current_indent == base_indent and current_item_lines:
            first_line = current_item_lines[0].strip()
            continuation = " ".join(l.strip() for l in current_item_lines[1:])
            items.append(f"{first_line} {continuation}".strip())
            current_item_lines = [line]
        else:
            current_item_lines.append(line)

    if current_item_lines:
        first_line = current_item_lines[0].strip()
        continuation = " ".join(l.strip() for l in current_item_lines[1:])
        items.append(f"{first_line} {continuation}".strip())

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
    base_indent = min(len(line) - len(line.lstrip()) for line in lines)

    items: list[tuple[str, str]] = []
    current_item_lines: list[str] = []

    for line in lines:
        current_indent = len(line) - len(line.lstrip())

        if current_indent == base_indent and current_item_lines:
            items.append(_build_structured_item(current_item_lines))
            current_item_lines = [line]
        else:
            current_item_lines.append(line)

    if current_item_lines:
        items.append(_build_structured_item(current_item_lines))

    return items


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
    header = re.sub(RE_PATTERN_SIMPLE_LIST_MARKER, "", item_lines[0].strip())
    description = " ".join(line.strip() for line in item_lines[1:])
    item = (header, description)

    return item
