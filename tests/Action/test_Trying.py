from ..utils import action, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_with_finally = results_formatter({
    (7, 0)
})

results_misc = results_formatter({
    (2, 0), (7, 0), (17, 4)
})

all_results = (results_with_finally | results_misc)


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Trying.py'))
    return engine


@pytest.mark.parametrize(('finally_'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Trying(grepper, action, consideration, finally_):
    if any([consideration, finally_]):
        action.reset()
        action.Trying.finally_ = finally_
        action.Trying.consideration = consideration
        grepper.add_constraint(action)
        results = all_results.copy()
        if finally_:
            results &= results_with_finally
        elif finally_ is False:
            results -= results_with_finally
        assert set(grepper.get_all_results()) == results


@pytest.mark.parametrize(('type_', 'result'), [
    (IndexError, {(2, 0), (7, 0)}),
    (AttributeError, {(7, 0)}),
    (Exception, {(17, 4)})
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Trying_Except_type(grepper, action, consideration, type_, result):
    action.reset()
    action.Trying.Except.type_ = type_
    action.Trying.Except.consideration = consideration
    grepper.add_constraint(action)
    assert set(grepper.get_all_results()) == results_formatter(result)


@pytest.mark.parametrize(('as_', 'result'), [
    ('e', results_with_finally),
    ('z', set([]))
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Trying_Except_as(grepper, action, consideration, as_, result):
    action.reset()
    action.Trying.Except.as_ = as_
    action.Trying.Except.consideration = consideration
    grepper.add_constraint(action)
    assert set(grepper.get_all_results()) == results_formatter(result)

@pytest.mark.parametrize(('type_'), [IndexError, AttributeError, Exception])
@pytest.mark.parametrize(('as_'), ['e', 'z'])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Trying_Except_type_as(grepper, action, consideration, type_, as_):
    action.reset()
    action.Trying.Except.type_ = type_
    action.Trying.Except.as_ = as_
    action.Trying.Except.consideration = consideration
    grepper.add_constraint(action)
    results = set([])
    if (type_ is IndexError) and (as_ == 'e'):
        results = results_with_finally
    assert set(grepper.get_all_results()) == results
