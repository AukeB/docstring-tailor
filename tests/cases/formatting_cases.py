"""Definitions for formatter test cases."""

from pathlib import Path
from itertools import chain

from tests.cases.config_model import Case, CaseTemplate, expand_template

CASE_TEMPLATES: list[CaseTemplate] = [
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/empty"),
        input_file_paths=[
            Path("empty_blank_lines.py"),
            Path("empty_no_space.py"),
            Path("empty_{line_length}.py"),
        ],
        output_file_path_template=Path("empty_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/paragraph_multi_line"),
        input_file_paths=[
            Path("paragraph_multi_line_wrong_input.py"),
            Path("paragraph_multi_line_{line_length}.py"),
        ],
        output_file_path_template=Path("paragraph_multi_line_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [60, 80, 100]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/paragraph_one_line"),
        input_file_paths=[
            Path("paragraph_one_line_wrong_input.py"),
            Path("paragraph_one_line_{line_length}.py"),
        ],
        output_file_path_template=Path("paragraph_one_line_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [60, 80, 100]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/code_block_singular"),
        input_file_paths=[
            Path("code_block_singular_blank_lines.py"),
            Path("code_block_singular_{line_length}.py"),
        ],
        output_file_path_template=Path("code_block_singular_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [80]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/code_block_multiple"),
        input_file_paths=[
            Path("code_block_multiple_blank_lines.py"),
            Path("code_block_multiple_{line_length}.py"),
        ],
        output_file_path_template=Path("code_block_multiple_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [80]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/code_repl_singular"),
        input_file_paths=[
            Path("code_repl_singular_blank_lines.py"),
            Path("code_repl_singular_{line_length}.py"),
        ],
        output_file_path_template=Path("code_repl_singular_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [80]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/code_repl_multiple"),
        input_file_paths=[
            Path("code_repl_multiple_blank_lines.py"),
            Path("code_repl_multiple_{line_length}.py"),
        ],
        output_file_path_template=Path("code_repl_multiple_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [80]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/structured_list"),
        input_file_paths=[
            Path("structured_list_wrong_input.py"),
            Path("structured_list_{line_length}.py"),
        ],
        output_file_path_template=Path("structured_list_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [60, 80, 100]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/simple_list"),
        input_file_paths=[
            Path("simple_list_wrong_input.py"),
            Path("simple_list_{line_length}.py"),
        ],
        output_file_path_template=Path("simple_list_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [60, 80, 100]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/named_paragraph_paragraph"),
        input_file_paths=[
            Path("named_paragraph_paragraph_wrong_input.py"),
            Path("named_paragraph_paragraph_{line_length}.py"),
        ],
        output_file_path_template=Path("named_paragraph_paragraph_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [60, 80, 100]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/named_paragraph_code_block"),
        input_file_paths=[
            Path("named_paragraph_code_block_blank_lines.py"),
            Path("named_paragraph_code_block_{line_length}.py"),
        ],
        output_file_path_template=Path("named_paragraph_code_block_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [80]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/named_paragraph_code_repl"),
        input_file_paths=[
            Path("named_paragraph_code_repl_blank_lines.py"),
            Path("named_paragraph_code_repl_{line_length}.py"),
        ],
        output_file_path_template=Path("named_paragraph_code_repl_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [80]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("docstring_elements/paragraph_and_simple_list"),
        input_file_paths=[
            Path("paragraph_and_simple_list_wrong_input.py"),
            Path("paragraph_and_simple_list_{line_length}.py"),
        ],
        output_file_path_template=Path("paragraph_and_simple_list_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [60, 80, 100]}
    ),
    CaseTemplate(
        fixture_directory_name=Path("function_docstring_complex"),
        input_file_paths=[
            Path("function_docstring_complex_60.py"),
            Path("function_docstring_complex_80.py"),
            Path("function_docstring_complex_100.py"),
        ],
        output_file_path_template=Path("function_docstring_complex_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [60, 80, 100]},
    ),
]

CASES: list[Case] = list(
    chain.from_iterable(expand_template(template) for template in CASE_TEMPLATES)
)
