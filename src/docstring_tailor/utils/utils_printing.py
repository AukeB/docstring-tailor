"""Utilities for printing and debugging docstring intermediate representations.

This module provides helper functions to render a parsed docstring IR tree as a
human-readable indented representation in the terminal. The output is intended
for debugging and inspection purposes rather than serialization.
"""

from docstring_tailor.defaults.ir_model import (
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


def print_docstring_ir(nodes: list[DocstringNode], indent: int = 0) -> None:
    """Pretty-print a docstring IR tree.

    Args:
        nodes (list[DocstringNode]): The list of top-level nodes in the
            docstring IR to print.
        indent (int, optional): The initial indentation level to apply to the
            printed output. Defaults to 0.
    """
    for node in nodes:
        print_node(node, indent)


def print_node(node: DocstringNode, indent: int = 0) -> None:
    """Print a single docstring IR node recursively.

    Args:
        node (DocstringNode): The docstring IR node to print.
        indent (int, optional): The indentation level used to represent the
            node's nesting depth in the output. Defaults to 0.
    """
    prefix = "  " * indent

    match node:
        case Paragraph(content):
            print(f"{prefix}Paragraph({content=})")

        case CodeBlock(code, delimiter):
            print(f"{prefix}CodeBlock({delimiter=}, {code=})")

        case CodeREPL(code):
            print(f"{prefix}CodeREPL({code=})")

        case StructuredList(keyword, entries):
            print(f"{prefix}StructuredList({keyword=})")
            for entry in entries:
                if isinstance(entry, StructuredListParameter):
                    print(f"{prefix}  {entry.name=}")
                    print(f"{prefix}  {entry.type=}")
                    print(f"{prefix}  {entry.description=}")
                elif isinstance(entry, StructuredListError):
                    print(f"{prefix}  {entry.error_type=}")
                    print(f"{prefix}  {entry.description=}")

        case SimpleList(list_type, items):
            print(f"{prefix}SimpleList({list_type=})")
            print(f"{prefix}  {items=}")

        case NamedParagraph(header, body):
            print(f"{prefix}NamedParagraph({header=})")
            print(f"{prefix}  {body=}")
            for child in body:
                print_node(child, indent + 1)

        case _:
            print(f"{prefix}{type(node).__name__}: {node}")
