"""Utilities for logging and debugging docstring intermediate representations.

This module provides helper functions to render a parsed docstring IR tree as a
human-readable indented representation in the log. The output is intended for
debugging and inspection purposes rather than serialization.
"""

import logging

from docstring_tailor.ir_model import (
    CodeBlock,
    CodeREPL,
    DocstringNode,
    NamedParagraph,
    Paragraph,
    SimpleList,
    StructuredList,
    StructuredListParameter,
)

logger = logging.getLogger(__name__)


def _print_node(node: DocstringNode, indent: int = 0) -> None:
    """Log a single docstring IR node recursively.

    Args:
        node (DocstringNode): The docstring IR node to print.
        indent (int, optional): The indentation level used to represent the
            node's nesting depth in the output. Defaults to 0.
    """

    prefix = "  " * indent

    match node:
        case Paragraph(content):
            logger.debug(f"{prefix}Paragraph({content=})")

        case CodeBlock(code, delimiter):
            logger.debug(f"{prefix}CodeBlock({delimiter=}, {code=})")

        case CodeREPL(code):
            logger.debug(f"{prefix}CodeREPL({code=})")

        case StructuredList(keyword, entries):
            logger.debug(f"{prefix}StructuredList({keyword=})")

            for entry in entries:
                if isinstance(entry, StructuredListParameter):
                    logger.debug(f"{prefix}  {entry.name=}")
                    logger.debug(f"{prefix}  {entry.type=}")
                    logger.debug(f"{prefix}  {entry.description=}")
                else:
                    logger.debug(f"{prefix}  {entry.error_type=}")
                    logger.debug(f"{prefix}  {entry.description=}")

        case SimpleList(list_type, items):
            logger.debug(f"{prefix}SimpleList({list_type=})")
            logger.debug(f"{prefix}  {items=}")

        case NamedParagraph(header, body):
            logger.debug(f"{prefix}NamedParagraph({header=})")
            logger.debug(f"{prefix}  {body=}")

            for child in body:
                _print_node(child, indent + 1)

        case _:
            node_name = type(node).__name__
            logger.debug(f"{prefix}{node_name}: {node}")


def _print_docstring_ir(nodes: list[DocstringNode], indent: int = 0) -> None:
    """Log a docstring IR tree at debug level.

    Args:
        nodes (list[DocstringNode]): The list of top-level nodes in the
            docstring IR to print.
        indent (int, optional): The initial indentation level to apply to the
            printed output. Defaults to 0.
    """

    for node in nodes:
        _print_node(node, indent)
