"""Tests for DocstringVisitor."""

import libcst as cst

from src.docstring_tailor.docstring_visitor import DocstringVisitor
from tests.mock_data.mock_data import (
    MODULE_DOCSTRING_NOT_SAME_LINE_EXPECTED,
    MODULE_DOCSTRING_NOT_SAME_LINE_INPUT,
    MODULE_DOCSTRING_TOO_LONG_EXPECTED,
    MODULE_DOCSTRING_TOO_LONG_INPUT,
)


def test_module_docstring_too_long() -> None:
    """Tests that a module docstring exceeding the line length is wrapped correctly."""
    input_tree = cst.parse_module(source=MODULE_DOCSTRING_TOO_LONG_INPUT)
    modified_tree = input_tree.visit(DocstringVisitor())

    assert modified_tree.code == MODULE_DOCSTRING_TOO_LONG_EXPECTED


def test_module_docstring_not_same_line() -> None:
    """Tests that a module docstring not starting on the same line as the triple quotes is fixed."""
    input_tree = cst.parse_module(source=MODULE_DOCSTRING_NOT_SAME_LINE_INPUT)
    modified_tree = input_tree.visit(DocstringVisitor())

    assert modified_tree.code == MODULE_DOCSTRING_NOT_SAME_LINE_EXPECTED