"""Case templates for the numpy fixtures."""

from pathlib import Path

from docstring_tailor.cli_config import DocstringStyle
from tests.cases.config_model import CaseTemplate

CASE_TEMPLATES_NUMPY: list[CaseTemplate] = [
    CaseTemplate(
        fixture_directory_name=Path(
            "numpy/docstring_elements/structured_list_malformed"
        ),
        input_file_paths=[Path("structured_list_malformed_wrong_input.py")],
        output_file_path_template=Path("structured_list_malformed_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "numpy/docstring_elements/named_paragraph_code_block"
        ),
        input_file_paths=[
            Path("named_paragraph_code_block_blank_lines.py"),
            Path("named_paragraph_code_block_{line_length}.py"),
        ],
        output_file_path_template=Path("named_paragraph_code_block_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "numpy/docstring_elements/named_paragraph_code_repl"
        ),
        input_file_paths=[
            Path("named_paragraph_code_repl_blank_lines.py"),
            Path("named_paragraph_code_repl_{line_length}.py"),
        ],
        output_file_path_template=Path("named_paragraph_code_repl_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "numpy/docstring_elements/named_paragraph_paragraph"
        ),
        input_file_paths=[
            Path("named_paragraph_paragraph_wrong_input.py"),
            Path("named_paragraph_paragraph_{line_length}.py"),
        ],
        output_file_path_template=Path("named_paragraph_paragraph_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "numpy/docstring_elements/paragraph_and_simple_list"
        ),
        input_file_paths=[
            Path("paragraph_and_simple_list_wrong_input.py"),
            Path("paragraph_and_simple_list_{line_length}.py"),
        ],
        output_file_path_template=Path("paragraph_and_simple_list_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("numpy/docstring_elements/structured_list"),
        input_file_paths=[
            Path("structured_list_wrong_input.py"),
            Path("structured_list_{line_length}.py"),
        ],
        output_file_path_template=Path("structured_list_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("numpy/module_docstring"),
        input_file_paths=[
            Path("module_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("module_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("numpy/class_docstring"),
        input_file_paths=[
            Path("class_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("class_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("numpy/function_docstring"),
        input_file_paths=[
            Path("function_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("function_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
]
