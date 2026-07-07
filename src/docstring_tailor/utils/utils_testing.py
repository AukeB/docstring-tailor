"""Utility module containing helper functions for testing purposes."""

from pathlib import Path

from docstring_tailor.defaults.constants import DIR_PATH_TEST_FIXTURES
from tests.cases.config_model import Case


def read_fixture(relative_file_path: Path) -> str:
    """Reads a fixture file and returns its contents.

    Args:
        relative_file_path (Path): Individual path components relative to the
            fixtures directory.

    Returns:
        file_content (str): The contents of the fixture file.
    """
    path = DIR_PATH_TEST_FIXTURES / relative_file_path
    file_content = path.read_text(encoding="utf-8")

    return file_content


def generate_case_ids(case: Case) -> str:
    """Generates a readable pytest parameter ID.

    The generated ID is displayed by pytest when parametrized tests run, making
    it easier to identify failing cases.

    Args:
        case (Case): The case for which the ID should be generated.

    Returns:
        case_id (str): A readable and deterministic pytest test ID.
    """
    parameter_settings = "_".join(
        f"{parameter_name}={parameter_value}"
        for parameter_name, parameter_value in sorted(case.parameters.items())
    )

    case_id = f"{case.input_file_path}__{case.output_file_path}__{parameter_settings}"

    return case_id
