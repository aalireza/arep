from ..utils import results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (3, 8), (5, 8), (10, 4), (12, 0)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Raising.py'))
    return engine


def test_Raising(grepper):
    grepper.add_constraint(hg.Action.Raising())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(("_error_type", "result"), [
    (TypeError, {(5, 8)}),
    (Exception, {(3, 8), (10, 4)}),
    (SystemExit, {(12, 0)}),
    (AttributeError, set([]))
])
def test_error_type(grepper, _error_type, result):
    grepper.add_constraint(hg.Action.Raising(_error_type=_error_type))
    assert set(grepper.get_all_results()) == results_formatter(result)


@pytest.mark.parametrize(("_error_message", "result"), [
    ("Something", {(3, 8)}),
    ("test", {(10, 4)}),
    ("Another test", set([]))
])
def test_error_message(grepper, _error_message, result):
    grepper.add_constraint(hg.Action.Raising(_error_message=_error_message))
    assert set(grepper.get_all_results()) == results_formatter(result)


@pytest.mark.parametrize(("_cause", "result"), [
    ("e", {(10, 4)}),
    ("d", set([]))
])
def test_cause(grepper, _cause, result):
    grepper.add_constraint(hg.Action.Raising(_cause=_cause))
    assert set(grepper.get_all_results()) == results_formatter(result)
