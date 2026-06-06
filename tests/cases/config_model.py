"""Models and utilities for declarative formatter test cases."""

from dataclasses import dataclass
from itertools import product
from typing import Any


@dataclass(frozen=True)
class Case:
    """Represents a single executable formatter test case.

    Attributes:
        input_file_path (str): The fixture file containing the unformatted source code.
        output_file_path (str): The fixture file containing the expected formatted output.
        parameters (dict[str, Any]): Configuration parameter values passed into
            ``DocstringVisitor``.
    """
    input_file_path: str
    output_file_path: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class CaseTemplate:
    """Defines a parametrized template used to generate multiple test cases.

    Attributes:
        input_file_path (str): The input fixture shared across all generated cases.
        output_file_path_template (str): A format string used to generate output fixture filenames.
        shared_parameters (dict[str, Any]): Configuration values shared across all generated cases.
            For example: 'module_docstring_{line_length}.py'
        parameter_grid (dict[str, list[Any]]): Defines the parametrized dimensions that should be
            expanded into concrete test cases. For example: '{"line_length": [60, 80, 100]}'
    """
    input_file_path: str
    output_file_path_template: str
    shared_parameters: dict[str, Any]
    parameter_grid: dict[str, list[Any]]


def expand_template(template: CaseTemplate) -> list[Case]:
    """Expands a ``CaseTemplate`` into concrete ``Case`` instances.

    The expansion is performed using a Cartesian product across all parameter_grid dimensions. Each
    unique combination produces a separate ``Case``.

    Args:
        template (CaseTemplate): The template definition to expand.

    Returns:
        list[Case]: A list of fully expanded executable test cases.
    """
    parameter_names = list(template.parameter_grid.keys())
    paramater_values = [template.parameter_grid[param_name] for param_name in parameter_names]
    cases: list[Case] = []

    for parameter_combinations in product(*paramater_values):
        parameter_grid_element = dict(zip(parameter_names, parameter_combinations))

        all_paramater_settings = {**template.shared_parameters, **parameter_grid_element} 
        output_file_path = template.output_file_path_template.format(**all_paramater_settings)

        case = Case(
            input_file_path=template.input_file_path,
            output_file_path=output_file_path,
            parameters=all_paramater_settings,
        )

        cases.append(case)

    return cases