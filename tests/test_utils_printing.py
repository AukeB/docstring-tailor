"""Tests for the IR debugging helpers in ``utils_printing``."""

import logging

import pytest

from docstring_tailor.ir_model import (
    CodeBlock,
    CodeREPL,
    DocstringNode,
    NamedParagraph,
    Paragraph,
    SimpleList,
    StructuredList,
    StructuredListError,
    StructuredListParameter,
)
from docstring_tailor.utils.utils_printing import _print_docstring_ir


class _UnknownNode(DocstringNode):
    """A node type the printer does not know about, used to reach its fallback branch."""


# Testing the "_print_docstring_ir" function.


def test_print_docstring_ir_logs_every_node_type(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Checks that each IR node type is logged at debug level with its fields."""
    nodes: list[DocstringNode] = [
        Paragraph(content="Summary."),
        CodeBlock(code="x = 1", delimiter="```"),
        CodeREPL(code=">>> x"),
        StructuredList(
            keyword="Args",
            entries=[
                StructuredListParameter(name="x", type="int", description="A value.")
            ],
        ),
        StructuredList(
            keyword="Raises",
            entries=[
                StructuredListError(error_type="ValueError", description="Bad input.")
            ],
        ),
        SimpleList(list_type="unordered", items=["one"], has_leading_blank_line=True),
        NamedParagraph(header="Note", body=[Paragraph(content="Inside.")]),
        _UnknownNode(),
    ]

    with caplog.at_level(logging.DEBUG, logger="docstring_tailor.utils.utils_printing"):
        _print_docstring_ir(nodes)

    messages = [record.getMessage() for record in caplog.records]

    assert any(message.startswith("Paragraph(") for message in messages)
    assert any(message.startswith("CodeBlock(") for message in messages)
    assert any(message.startswith("CodeREPL(") for message in messages)
    assert any("StructuredList(keyword='Args')" in message for message in messages)
    assert any("error_type='ValueError'" in message for message in messages)
    assert any(message.startswith("SimpleList(") for message in messages)
    assert any(message.startswith("NamedParagraph(") for message in messages)
    assert any(message.startswith("  Paragraph(") for message in messages)
    assert any(message.startswith("_UnknownNode: ") for message in messages)
