"""Formatter test cases, grouped by the fixture folder they read from.

Each module in this package holds the case templates for one category. The
templates are expanded into concrete cases and exported as ``CASES``.
"""

from itertools import chain

from tests.cases.config_model import Case, CaseTemplate, expand_template
from tests.cases.formatting_cases.convert import CASE_TEMPLATES_CONVERT
from tests.cases.formatting_cases.google import CASE_TEMPLATES_GOOGLE
from tests.cases.formatting_cases.numpy import CASE_TEMPLATES_NUMPY
from tests.cases.formatting_cases.sphinx import CASE_TEMPLATES_SPHINX

CASE_TEMPLATES: list[CaseTemplate] = (
    CASE_TEMPLATES_GOOGLE
    + CASE_TEMPLATES_NUMPY
    + CASE_TEMPLATES_SPHINX
    + CASE_TEMPLATES_CONVERT
)

expanded_cases = [expand_template(template) for template in CASE_TEMPLATES]
flattened_cases = chain.from_iterable(expanded_cases)

CASES: list[Case] = list(flattened_cases)
