"""Tests for DocstringVisitor."""

from pathlib import Path

import libcst as cst

from docstring_tailor.docstring_visitor import DocstringVisitor

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def read_fixture(*path_parts: str) -> str:
    """Reads a fixture file and returns its contents."""
    path = FIXTURES_DIR.joinpath(*path_parts)
    return path.read_text(encoding="utf-8")


def test_module_docstring_too_long() -> None:
    """Tests that overly long docstrings are formatted correctly."""
    input_code = read_fixture("raw", "all_docstring_types_too_long.py")
    expected_code = read_fixture("formatted", "all_docstring_types_100.py")

    input_tree = cst.parse_module(source=input_code)
    modified_tree = input_tree.visit(DocstringVisitor(line_length=100))

    assert modified_tree.code == expected_code


def test_module_docstring_too_short() -> None:
    """Tests that short docstrings are formatted correctly."""
    input_code = read_fixture("raw", "all_docstring_types_too_short.py")
    expected_code = read_fixture("formatted", "all_docstring_types_100.py")

    input_tree = cst.parse_module(source=input_code)
    modified_tree = input_tree.visit(DocstringVisitor(line_length=100))

    assert modified_tree.code == expected_code