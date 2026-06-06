"""Definitions for formatter test cases."""

from tests.cases.config_model import Case, CaseTemplate, expand_template


CASES: list[Case] = [
    *expand_template(
        CaseTemplate(
            input_file_path="all_too_long.py",
            output_file_path_template="all_{line_length}.py",
            shared_parameters={},
            parameter_grid={
                "line_length": [60, 80, 100],
            },
        )
    ),
    *expand_template(
        CaseTemplate(
            input_file_path="all_too_short.py",
            output_file_path_template="all_{line_length}.py",
            shared_parameters={},
            parameter_grid={
                "line_length": [60, 80, 100],
            },
        )
    ),
]