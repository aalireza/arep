from ..utils import action, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_for_else = results_formatter({
    (15, 0)
})

results_with_break = results_formatter({
    (21, 0), (22, 4), (27, 0), (34, 4)
})

results_infinite = results_formatter({
    (21, 0), (40, 4), (34, 4)
})

results_for = results_formatter({
    (1, 0), (15, 0), (2, 4), (8, 4), (11, 4), (13, 5), (22, 4)
})

results_while = results_formatter({
    (21, 0), (27, 0), (33, 0), (39, 0), (34, 4), (40, 4)
})

all_results = set(results_for | results_while)


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Looping.py'))
    return engine

@pytest.mark.parametrize(('non_terminating'), [True, False, None])
@pytest.mark.parametrize(('with_break'), [True, False, None])
@pytest.mark.parametrize(('for_else'), [True, False, None])
@pytest.mark.parametrize(('while_'), [True, False, None])
@pytest.mark.parametrize(('for_'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Looping(grepper, action, consideration,
                 for_, while_, for_else, with_break, non_terminating):
    if any([consideration, for_, while_, for_else, with_break,
            non_terminating]):
        action.reset()
        results = set()
        action.Looping.consideration = consideration
        action.Looping.for_ = for_
        action.Looping.while_ = while_
        action.Looping.for_else = for_else
        action.Looping.with_break = with_break
        action.Looping.with_simple_non_terminating_test = non_terminating
        if consideration is not False:
            results = all_results.copy()
        if for_:
            results &= results_for
        elif for_ is False:
            results -= results_for
        if while_:
            results &= results_while
        elif while_ is False:
            results -= results_while
        if for_else:
            results &= results_for_else
        elif for_else is False:
            results -= results_for_else
        if with_break:
            results &= results_with_break
        elif with_break is False:
            results -= results_with_break
        if non_terminating:
            results &= results_infinite
        elif non_terminating is False:
            results -= results_infinite
        if any([for_, for_else]) and while_:
            results = set()
        grepper.add_constraint(action)
        assert set(grepper.get_all_results()) == results
