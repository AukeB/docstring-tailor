"""Tests for ``DocstringVisitor``."""

import libcst as cst
import pytest

from docstring_tailor.docstring_visitor import DocstringVisitor
from tests.cases.config_model import Case
from tests.cases.formatting_cases import CASES
from tests.utils_test import generate_case_ids, read_fixture


@pytest.mark.parametrize("case", CASES, ids=generate_case_ids)
def test_formatting(case: Case) -> None:
    """Tests formatter output against expected golden files.

    Args:
        case (Case): The test case containing fixture paths and formatter configuration.
    """
    input_code = read_fixture(case.input_file_path)
    expected_code = read_fixture(case.output_file_path)
    input_tree = cst.parse_module(source=input_code)
    modified_tree = input_tree.visit(DocstringVisitor(**case.parameters))

    assert modified_tree.code == expected_code
