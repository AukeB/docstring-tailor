"""Models and utilities for declarative formatter test cases."""

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Case:
    """Represents a single executable formatter test case.

    Attributes:
        input_file_path (Path): The fixture file containing the unformatted source code.
        output_file_path (Path): The fixture file containing the expected formatted output.
        parameters (dict[str, Any]): Configuration parameter values passed into
            ``DocstringVisitor``.
    """

    input_file_path: Path
    output_file_path: Path
    parameters: dict[str, Any]


@dataclass(frozen=True)
class CaseTemplate:
    """Defines a parametrized template used to generate multiple test cases.

    Attributes:
        fixture_directory_name (Path): Name of the directory where the fixtures are stored.
        input_file_path (Path | list[Path]): The input fixture(s) shared across all generated cases.
        output_file_path_template (Path): A format string used to generate output fixture filenames.
        shared_parameters (dict[str, Any]): Configuration values shared across all generated cases.
            For example: 'module_docstring_{line_length}.py'
        parameter_grid (dict[str, list[Any]]): Defines the parametrized dimensions that should be
            expanded into concrete test cases. For example: '{"line_length": [60, 80, 100]}'
    """

    fixture_directory_name: Path
    input_file_paths: Path | list[Path]
    output_file_path_template: Path
    shared_parameters: dict[str, Any]
    parameter_grid: dict[str, list[Any]]


def expand_input_file_paths(
    input_file_paths: Path | list[Path],
    parameter_grid: dict[str, list[Any]],
) -> list[Path]:
    """Expands templated input fixture paths into concrete paths.

    Input paths may be either literal paths or format-string templates containing
    placeholders corresponding to keys in ``parameter_grid``. Literal paths are returned
    unchanged, while templated paths are expanded using the Cartesian product of all
    parameter values.

    Args:
        input_file_paths (Path | list[Path]): One or more input fixture paths, each of which
            may optionally contain format placeholders.
        parameter_grid (dict[str, list[Any]]): The parameter dimensions used to expand
            templated paths.

    Returns:
        list[Path]: A list containing all concrete input fixture paths.
    """
    if isinstance(input_file_paths, Path):
        input_file_paths = [input_file_paths]

    parameter_names = list(parameter_grid)
    parameter_values = [
        parameter_grid[name]
        for name in parameter_names
    ]

    expanded: list[Path] = []

    for input_file_path in input_file_paths:
        path_string = str(input_file_path)

        if "{" not in path_string:
            expanded.append(input_file_path)
            continue

        for combination in product(*parameter_values):
            parameters = dict(zip(parameter_names, combination))
            expanded.append(
                Path(path_string.format(**parameters))
            )

    return expanded


def expand_template(template: CaseTemplate) -> list[Case]:
    """Expands a ``CaseTemplate`` into concrete ``Case`` instances.

    The expansion is performed using a Cartesian product across all parameter_grid dimensions. Each
    unique combination produces a separate ``Case``.

    Args:
        template (CaseTemplate): The template definition to expand.

    Returns:
        list[Case]: A list of fully expanded executable test cases.
    """
    fixture_directory_name = template.fixture_directory_name

    input_file_paths = expand_input_file_paths(
        template.input_file_paths,
        template.parameter_grid,
    )

    parameter_names = list(template.parameter_grid.keys())
    paramater_values = [
        template.parameter_grid[param_name] for param_name in parameter_names
    ]
    
    cases: list[Case] = []

    if isinstance(input_file_paths, Path):
        input_file_paths = [input_file_paths]

    for input_file_path in input_file_paths:
        for parameter_combinations in product(*paramater_values):
            parameter_grid_element = dict(zip(parameter_names, parameter_combinations))

            all_paramater_settings = {
                **template.shared_parameters,
                **parameter_grid_element,
            }
            output_file_path = Path(
                str(template.output_file_path_template).format(**all_paramater_settings)
            )

            case = Case(
                input_file_path=fixture_directory_name / input_file_path,
                output_file_path=fixture_directory_name / output_file_path,
                parameters=all_paramater_settings,
            )

            cases.append(case)

    return cases
