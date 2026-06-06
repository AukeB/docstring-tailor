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
        ],
        output_file_path_template=Path("all_docstrings_{line_length}.py"),
        shared_parameters={"detect_lists": True},
        parameter_grid={
            "line_length": [60, 80, 100],
        },
    ),
    CaseTemplate(
        fixture_directory_name=Path("module_docstrings"),
        input_file_paths=Path("module_docstring_ordered_list.py"),
        output_file_path_template=Path(
            "module_docstring_ordered_list_{line_length}.py"
        ),
        shared_parameters={"detect_lists": True},
        parameter_grid={
            "line_length": [100],
        },
    ),
]

CASES: list[Case] = list(
    chain.from_iterable(expand_template(template) for template in CASE_TEMPLATES)
)
