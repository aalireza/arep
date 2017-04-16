from ..utils import action, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_with_elif = results_formatter({
    (2, 0), (13, 0)
})

results_with_else = results_formatter({
    (2, 0), (11, 5)
})

results_is_ifexp = results_formatter({
    (11, 5)
})

results_in_comprehensions = results_formatter({
    (18, 10), (20, 11), (23, 4), (23, 16)
})

misc_results = results_formatter({
    (30, 4)
})

all_results = (misc_results | results_with_elif | results_with_else |
               results_is_ifexp | results_in_comprehensions)


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Conditional.py'))
    return engine


@pytest.mark.parametrize(('elif_'), [True, False, None])
@pytest.mark.parametrize(('else_'), [True, False, None])
@pytest.mark.parametrize(('ifexp'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Conditional(grepper, action, consideration, elif_, else_, ifexp):
    if any([consideration, elif_, else_, ifexp]):
        action.reset()
        action.Conditional.consideration = consideration
        action.Conditional.else_ = else_
        action.Conditional.elif_ = elif_
        action.Conditional.ifexp = ifexp
        grepper.add_constraint(action)
        obtained_results = set(grepper.get_all_results())
        if ifexp is None:
            target_results = all_results.copy()
        elif ifexp is True:
            target_results = results_is_ifexp.copy()
        elif ifexp is False:
            target_results = (all_results - results_is_ifexp)
        if elif_ is True:
            target_results &= results_with_elif
        elif elif_ is False:
            target_results -= results_with_elif
        if else_ is True:
            target_results &= results_with_else
        elif else_ is False:
            target_results -= results_with_else
        assert obtained_results == target_results
