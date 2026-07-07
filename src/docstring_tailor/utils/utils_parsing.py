"""Utility functions for parsing docstring section content."""

import re

from docstring_tailor.defaults.constants import RE_PATTERN_LIST_MARKER


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

    items = [re.sub(RE_PATTERN_LIST_MARKER, "", item) for item in items]

    return items
