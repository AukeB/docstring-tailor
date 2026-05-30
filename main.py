"""Main module"""

import libcst as cst

from src.docstring_tailor.docstring_visitor import DocstringVisitor
from src.docstring_tailor.constants import FILE_PATH_INPUT, FILE_PATH_OUTPUT, ENCODING, STYLE


def main():
    """Main function"""
    if STYLE != "Google":
        raise ValueError("Unsupported docstring format detected.")

    # Input
    input_data = FILE_PATH_INPUT.read_text(encoding=ENCODING)
    input_tree = cst.parse_module(source=input_data)

    # Process
    modified_tree = input_tree.visit(DocstringVisitor())

    # Output
    output_data = modified_tree.code
    FILE_PATH_OUTPUT.write_text(output_data, encoding=ENCODING)


if __name__ == "__main__":
    main()