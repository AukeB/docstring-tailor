"""Main module"""

import libcst as cst

from pathlib import Path

from src.docstring_tailor.docstring_visitor import DocstringVisitor
from src.docstring_tailor.constants import DIRECTORY_PATH_INPUT, ENCODING, STYLE


def main():
    """Main function"""
    if STYLE != "Google":
        raise ValueError("Unsupported docstring format detected.")

    input_file_paths = DIRECTORY_PATH_INPUT.glob(pattern="*.py")

    for input_file_path in input_file_paths:
        input_data = input_file_path.read_text(encoding=ENCODING)
        input_tree = cst.parse_module(source=input_data)

        # Process
        modified_tree = input_tree.visit(DocstringVisitor())

        # Output
        output_data = modified_tree.code
        output_file_path = Path(str(input_file_path).replace("input", "output"))
        output_file_path.write_text(output_data, encoding=ENCODING)


if __name__ == "__main__":
    main()


"""
Not tested yet:
- Different indentation levels
- Low line length values
"""