"""Case templates for the convert fixtures."""

from pathlib import Path

from docstring_tailor.cli_config import DocstringStyle
from tests.cases.config_model import CaseTemplate

CASE_TEMPLATES_CONVERT: list[CaseTemplate] = [
    CaseTemplate(
        fixture_directory_name=Path("convert/google_to_numpy"),
        input_file_paths=[
            Path("function_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("function_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.google,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("convert/numpy_to_google"),
        input_file_paths=[
            Path("function_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("function_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.google,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("convert/sphinx_to_google"),
        input_file_paths=[
            Path("function_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("function_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.google,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("convert/sphinx_to_numpy"),
        input_file_paths=[
            Path("function_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("function_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("convert/google_to_sphinx"),
        input_file_paths=[
            Path("function_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("function_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.google,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path("convert/numpy_to_sphinx"),
        input_file_paths=[
            Path("function_docstring_wrong_input.py"),
        ],
        output_file_path_template=Path("function_docstring_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.numpy,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "convert/sphinx_to_google/docstring_elements/structured_list_untyped"
        ),
        input_file_paths=[Path("structured_list_untyped_wrong_input.py")],
        output_file_path_template=Path("structured_list_untyped_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.google,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "convert/sphinx_to_numpy/docstring_elements/structured_list_untyped"
        ),
        input_file_paths=[Path("structured_list_untyped_wrong_input.py")],
        output_file_path_template=Path("structured_list_untyped_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.sphinx,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "convert/google_to_numpy/docstring_elements/structured_list_malformed"
        ),
        input_file_paths=[Path("structured_list_malformed_wrong_input.py")],
        output_file_path_template=Path("structured_list_malformed_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.google,
            "to_style": DocstringStyle.numpy,
        },
        parameter_grid={"line_length": [80]},
    ),
    CaseTemplate(
        fixture_directory_name=Path(
            "convert/google_to_sphinx/docstring_elements/structured_list_malformed"
        ),
        input_file_paths=[Path("structured_list_malformed_wrong_input.py")],
        output_file_path_template=Path("structured_list_malformed_{line_length}.py"),
        shared_parameters={
            "from_style": DocstringStyle.google,
            "to_style": DocstringStyle.sphinx,
        },
        parameter_grid={"line_length": [80]},
    ),
]
