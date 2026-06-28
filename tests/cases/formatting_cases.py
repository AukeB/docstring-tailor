"""Definitions for formatter test cases."""

from pathlib import Path
from itertools import chain

from tests.cases.config_model import Case, CaseTemplate, expand_template

CASE_TEMPLATES: list[CaseTemplate] = [
    CaseTemplate(
        fixture_directory_name=Path("all_docstrings"),
        input_file_paths=[
            Path("all_docstrings_too_short.py"),
            Path("all_docstrings_too_long.py"),
            Path("all_docstrings_60.py"), #TODO: Also implement _{line_length} functionality for input files.
            Path("all_docstrings_80.py"),
            Path("all_docstrings_100.py"),
        ],
        output_file_path_template=Path("all_docstrings_{line_length}.py"),
        shared_parameters={},
        parameter_grid={"line_length": [60, 80, 100]},
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
    CaseTemplate(
        fixture_directory_name=Path("module_docstring_blank_lines"),
        input_file_paths=Path("module_docstring_blank_lines.py"),
        output_file_path_template=Path("module_docstring_blank_lines_100.py"),
        shared_parameters={"line_length": 100},
        parameter_grid={},
    ),
    CaseTemplate(
        fixture_directory_name=Path("module_docstring_empty"),
        input_file_paths=[
            Path("module_docstring_empty.py"),
            Path("module_docstring_empty_blank_lines.py"),
        ],
        output_file_path_template=Path("module_docstring_empty.py"),
        shared_parameters={"line_length": 100},
        parameter_grid={},
    ),
    # CaseTemplate(
    #     fixture_directory_name=Path("module_docstring_example_backticks"),
    #     input_file_paths=[
    #         Path("module_docstring_example_backticks.py"),
    #         Path("module_docstring_example_backticks_60.py"),
    #     ],
    #     output_file_path_template=Path("module_docstring_example_backticks_60.py"),
    #     shared_parameters={"line_length": 60},
    #     parameter_grid={},
    # ),
    # CaseTemplate(
    #     fixture_directory_name=Path("module_docstring_example_tildes"),
    #     input_file_paths=[
    #         Path("module_docstring_example_tildes.py"),
    #         Path("module_docstring_example_tildes_60.py"),
    #     ],
    #     output_file_path_template=Path("module_docstring_example_tildes_60.py"),
    #     shared_parameters={"line_length": 60},
    #     parameter_grid={},
    # ),
    # CaseTemplate(
    #     fixture_directory_name=Path("module_docstring_ordered_list"),
    #     input_file_paths=[
    #         Path("module_docstring_ordered_list_too_long.py"),
    #         Path("module_docstring_ordered_list_60.py"),
    #         Path("module_docstring_ordered_list_80.py"),
    #         Path("module_docstring_ordered_list_100.py"),
    #     ],
    #     output_file_path_template=Path(
    #         "module_docstring_ordered_list_{line_length}.py"
    #     ),
    #     shared_parameters={},
    #     parameter_grid={
    #         "line_length": [60, 80, 100],
    #     },
    # ),
    # CaseTemplate(
    #     fixture_directory_name=Path("module_docstring_repl_and_codeblock"),
    #     input_file_paths=[
    #         Path("module_docstring_repl_and_codeblock_60.py"),
    #         Path("module_docstring_repl_and_codeblock_80.py"),
    #         Path("module_docstring_repl_and_codeblock_100.py"),
    #     ],
    #     output_file_path_template=Path(
    #         "module_docstring_repl_and_codeblock_{line_length}.py"
    #     ),
    #     shared_parameters={},
    #     parameter_grid={
    #         "line_length": [60, 80, 100],
    #     },
    # )
]

CASES: list[Case] = list(
    chain.from_iterable(expand_template(template) for template in CASE_TEMPLATES)
)
