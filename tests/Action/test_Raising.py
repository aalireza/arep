from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (3, 8), (5, 8), (10, 4), (12, 0)
})


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Raising.py'))
    return engine


def test_Raising(grepper, action):
    action.reset()
    action.Raising.consideration = True
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == all_results


@pytest.mark.parametrize(("type_", "result"), [
    (TypeError, {(5, 8)}),
    (Exception, {(3, 8), (10, 4)}),
    (SystemExit, {(12, 0)}),
    (AttributeError, set([]))
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Error_type(grepper, action, consideration, type_, result):
    action.reset()
    action.Raising.Error.type_ = type_
    action.Raising.Error.consideration = consideration
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(result)


@pytest.mark.parametrize(("message", "result"), [
    ("Something", {(3, 8)}),
    ("test", {(10, 4)}),
    ("Another test", set([]))
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Error_message(grepper, action, consideration, message, result):
    action.reset()
    action.Raising.Error.message = message
    action.Raising.Error.consideration = consideration
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(result)


@pytest.mark.parametrize(("message"), ["Something", "test", "spam"])
@pytest.mark.parametrize(("type_"), [Exception, TypeError])
def test_Error_message_type(grepper, action, message, type_):
    action.reset()
    action.Raising.Error.type_ = type_
    action.Raising.Error.message = message
    grepper.constraint_list.append(action)
    results = set([])
    if bool(type_ is Exception):
        if (message == "Something"):
            results = results_formatter({(3, 8)})
        elif (message == "test"):
            results = results_formatter({(10, 4)})
    assert set(grepper.all_results()) == results_formatter(results)

@pytest.mark.parametrize(("name", "result"), [
    ("e", {(10, 4)}),
    ("d", set([]))
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Cause_name(grepper, action, consideration, name, result):
    action.reset()
    action.Raising.Cause.name = name
    action.Raising.Cause.consideration = consideration
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(result)


@pytest.mark.parametrize(('type_'), [Exception, SystemExit, None])
@pytest.mark.parametrize(('message'), ["test", "Something", None])
@pytest.mark.parametrize(('name'), ["e", "f"])
def test_Cause_name_Error_message_type(grepper, action, name, message,
                                       type_):
    action.reset()
    action.Raising.Cause.name = name
    action.Raising.Error.type_ = type_
    action.Raising.Error.message = message
    grepper.constraint_list.append(action)
    results = results_formatter({(10, 4)})
    if (
            (type_ not in {Exception, None}) or
            (message not in {"test", None}) or
            (name != 'e')
    ):
        results = set([])
    assert set(grepper.all_results()) == results
