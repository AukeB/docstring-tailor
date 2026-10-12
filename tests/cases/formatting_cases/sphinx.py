"""Case templates for the sphinx fixtures."""

from pathlib import Path

from docstring_tailor.cli_config import DocstringStyle
from tests.cases.config_model import CaseTemplate

CASE_TEMPLATES_SPHINX: list[CaseTemplate] = [
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/empty"),
        input_file_paths=[
            Path("empty_wrong_input.py"),
        ],
        output_file_path_template=Path("empty_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/paragraph_one_line"),
        input_file_paths=[
            Path("paragraph_one_line_wrong_input.py"),
        ],
        output_file_path_template=Path("paragraph_one_line_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/paragraph_multi_line"),
        input_file_paths=[
            Path("paragraph_multi_line_wrong_input.py"),
        ],
        output_file_path_template=Path("paragraph_multi_line_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "sphinx/docstring_elements/paragraph_and_simple_list"
        ),
        input_file_paths=[
            Path("paragraph_and_simple_list_wrong_input.py"),
        ],
        output_file_path_template=Path("paragraph_and_simple_list_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/simple_list"),
        input_file_paths=[
            Path("simple_list_wrong_input.py"),
        ],
        output_file_path_template=Path("simple_list_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/code_block_singular"),
        input_file_paths=[
            Path("code_block_singular_wrong_input.py"),
        ],
        output_file_path_template=Path("code_block_singular_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/code_block_multiple"),
        input_file_paths=[
            Path("code_block_multiple_wrong_input.py"),
        ],
        output_file_path_template=Path("code_block_multiple_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/code_repl_singular"),
        input_file_paths=[
            Path("code_repl_singular_wrong_input.py"),
        ],
        output_file_path_template=Path("code_repl_singular_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/code_repl_multiple"),
        input_file_paths=[
            Path("code_repl_multiple_wrong_input.py"),
        ],
        output_file_path_template=Path("code_repl_multiple_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "sphinx/docstring_elements/named_paragraph_paragraph"
        ),
        input_file_paths=[
            Path("named_paragraph_paragraph_wrong_input.py"),
        ],
        output_file_path_template=Path("named_paragraph_paragraph_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "sphinx/docstring_elements/named_paragraph_code_block"
        ),
        input_file_paths=[
            Path("named_paragraph_code_block_wrong_input.py"),
        ],
        output_file_path_template=Path("named_paragraph_code_block_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "sphinx/docstring_elements/named_paragraph_code_repl"
        ),
        input_file_paths=[
            Path("named_paragraph_code_repl_wrong_input.py"),
        ],
        output_file_path_template=Path("named_paragraph_code_repl_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/structured_list"),
        input_file_paths=[
            Path("structured_list_wrong_input.py"),
        ],
        output_file_path_template=Path("structured_list_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "sphinx/docstring_elements/structured_list_malformed"
        ),
        input_file_paths=[
            Path("structured_list_malformed_wrong_input.py"),
        ],
        output_file_path_template=Path("structured_list_malformed_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/module_docstring"),
        input_file_paths=[
            Path("module_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("module_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/class_docstring"),
        input_file_paths=[
            Path("class_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("class_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/function_docstring"),
        input_file_paths=[
            Path("function_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("function_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "sphinx/docstring_elements/structured_list_partial"
        ),
        input_file_paths=[Path("structured_list_partial_wrong_input.py")],
        output_file_path_template=Path("structured_list_partial_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("sphinx/docstring_elements/named_paragraph_empty"),
        input_file_paths=[Path("named_paragraph_empty_wrong_input.py")],
        output_file_path_template=Path("named_paragraph_empty_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [60, 80, 100]},
    ),
]
