from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_with_msg = results_formatter({(2, 0), (5, 4)})
all_results = results_formatter({(1, 0), (2, 0), (5, 4)})


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Assertion.py'))
    return engine


@pytest.mark.parametrize(('error'), [True, False, None])
@pytest.mark.parametrize(('assertion'), [True, False, None])
def test_Assertion(grepper, action, error, assertion):
    action.reset()
    results = set()
    if any([error, assertion]):
        action.Assertion.consideration = assertion
        action.Assertion.Error.consideration = error
        if assertion is not False:
            results = all_results.copy()
        if error:
            results &= results_with_msg
        elif error is False:
            results -= results_with_msg
        grepper.constraint_list.append(action)
        assert set(grepper.all_results()) == results_formatter(results)


@pytest.mark.parametrize(("msg", "result"), [
    ("test", {(2, 0)}),
    ("nested test", {(5, 4)}),
    ("not there", {})
])
def test_Assertion_with_error_msg(grepper, action, msg, result):
    action.reset()
    action.Assertion.Error.content = msg
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(result)
