"""Models and utilities for declarative formatter test cases."""

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import TypedDict, cast

from docstring_tailor.cli_config import DocstringStyle


class CaseParameters(TypedDict):
    """Configuration values passed into ``DocstringVisitor`` for one test case.

    Attributes:
        line_length (int): The maximum line length to wrap docstrings to.
        from_style (DocstringStyle): The style the docstrings are parsed as.
        to_style (DocstringStyle): The style the docstrings are rendered as.
    """

    line_length: int
    from_style: DocstringStyle
    to_style: DocstringStyle


class SharedParameters(TypedDict):
    """Configuration values shared by every case generated from one template.

    Attributes:
        from_style (DocstringStyle): The style the docstrings are parsed as.
        to_style (DocstringStyle): The style the docstrings are rendered as.
    """

    from_style: DocstringStyle
    to_style: DocstringStyle


class ParameterGrid(TypedDict):
    """Parametrized dimensions that are expanded into concrete test cases.

    Attributes:
        line_length (list[int]): The line lengths to generate one case for each.
    """

    line_length: list[int]


@dataclass(frozen=True)
class Case:
    """Represents a single executable formatter test case.

    Attributes:
        input_file_path (Path): The fixture file containing the unformatted source code.
        output_file_path (Path): The fixture file containing the expected formatted output.
        parameters (CaseParameters): Configuration parameter values passed into
            ``DocstringVisitor``.
    """

    input_file_path: Path
    output_file_path: Path
    parameters: CaseParameters


@dataclass(frozen=True)
class CaseTemplate:
    """Defines a parametrized template used to generate multiple test cases.

    Attributes:
        fixture_directory_name (Path): Name of the directory where the fixtures are stored.
        input_file_path (Path | list[Path]): The input fixture(s) shared across all generated cases.
        output_file_path_template (Path): A format string used to generate output fixture filenames.
        shared_parameters (SharedParameters): Configuration values shared across all generated cases.
        parameter_grid (ParameterGrid): Defines the parametrized dimensions that should be
            expanded into concrete test cases. For example: '{"line_length": [60, 80, 100]}'
    """

    fixture_directory_name: Path
    input_file_paths: Path | list[Path]
    output_file_path_template: Path
    shared_parameters: SharedParameters
    parameter_grid: ParameterGrid


def expand_input_file_paths(
    input_file_paths: Path | list[Path],
    parameter_grid: dict[str, list[int]],
) -> list[Path]:
    """Expands templated input fixture paths into concrete paths.

    Input paths may be either literal paths or format-string templates containing
    placeholders corresponding to keys in ``parameter_grid``. Literal paths are returned
    unchanged, while templated paths are expanded using the Cartesian product of all
    parameter values.

    Args:
        input_file_paths (Path | list[Path]): One or more input fixture paths, each of which
            may optionally contain format placeholders.
        parameter_grid (dict[str, list[int]]): The parameter dimensions used to expand
            templated paths.

    Returns:
        expanded (list[Path]): A list containing all concrete input fixture paths.
    """

    if isinstance(input_file_paths, Path):
        input_file_paths = [input_file_paths]

    parameter_names = list(parameter_grid)
    parameter_values = [parameter_grid[name] for name in parameter_names]

    expanded: list[Path] = []

    for input_file_path in input_file_paths:
        path_string = str(input_file_path)

        if "{" not in path_string:
            expanded.append(input_file_path)

            continue

        for combination in product(*parameter_values):
            pairs = zip(parameter_names, combination)
            parameters = dict(pairs)

            formatted_path = path_string.format(**parameters)
            expanded_path = Path(formatted_path)

            expanded.append(expanded_path)

    return expanded


def expand_template(template: CaseTemplate) -> list[Case]:
    """Expands a ``CaseTemplate`` into concrete ``Case`` instances.

    The expansion is performed using a Cartesian product across all parameter_grid dimensions. Each
    unique combination produces a separate ``Case``.

    Args:
        template (CaseTemplate): The template definition to expand.

    Returns:
        cases (list[Case]): A list of fully expanded executable test cases.
    """

    fixture_directory_name = template.fixture_directory_name

    # A TypedDict cannot be indexed by a computed key, so the grid is viewed as a
    # plain mapping of parameter name to values. Its keys are the TypedDict's keys.
    parameter_grid = cast(dict[str, list[int]], template.parameter_grid)

    input_file_paths = expand_input_file_paths(
        template.input_file_paths,
        parameter_grid,
    )

    parameter_names = list(parameter_grid)
    parameter_values = [parameter_grid[param_name] for param_name in parameter_names]

    cases: list[Case] = []

    if isinstance(input_file_paths, Path):
        input_file_paths = [input_file_paths]

    for input_file_path in input_file_paths:
        for parameter_combinations in product(*parameter_values):
            pairs = zip(parameter_names, parameter_combinations)
            parameter_grid_element = dict(pairs)

            # The shared values and the grid values together hold every key of
            # CaseParameters, so the merged dict has exactly that shape.
            merged_settings = {
                **template.shared_parameters,
                **parameter_grid_element,
            }
            all_parameter_settings = cast(CaseParameters, merged_settings)

            output_template = str(template.output_file_path_template)
            formatted_output = output_template.format(**all_parameter_settings)
            output_file_path = Path(formatted_output)

            case = Case(
                input_file_path=fixture_directory_name / input_file_path,
                output_file_path=fixture_directory_name / output_file_path,
                parameters=all_parameter_settings,
            )

            cases.append(case)

    return cases
