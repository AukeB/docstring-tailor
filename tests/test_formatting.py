"""Tests for ``DocstringVisitor``."""

import pytest
import libcst as cst

from tests.cases.formatting_cases import CASES
from tests.cases.config_model import Case
from tests.utils_test import read_fixture, generate_case_ids
from docstring_tailor.docstring_visitor import DocstringVisitor


@pytest.mark.parametrize("case", CASES, ids=generate_case_ids)
def test_formatting(case: Case) -> None:
    """Tests formatter output against expected golden files.

    Args:
        case (Case): The test case containing fixture paths and formatter configuration.
    """
    input_code = read_fixture("raw", case.input_file_path)
    expected_code = read_fixture("formatted", case.output_file_path)
    input_tree = cst.parse_module(source=input_code)
    modified_tree = input_tree.visit(DocstringVisitor(**case.parameters))

    assert modified_tree.code == expected_code