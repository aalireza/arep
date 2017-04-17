from ..utils import kind, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_regular = results_formatter({
    (4, 0), (7, 0), (22, 0), (6, 0), (23, 6)
})

results_temp = results_formatter({
    (1, 4), (2, 10)
})

results_args = results_formatter({
    (6, 19), (7, 16), (15, 23), (10, 6), (10, 9), (15, 17), (18, 19),
})

results_attributes = results_formatter({
    (16, 8), (19, 15), (23, 22)
})

results_originally_arg = results_formatter({
    (6, 22), (7, 19), (11, 23), (11, 21), (11, 17), (11, 15), (16, 21)
})

all_results = (results_regular | results_temp | results_args |
               results_attributes | results_originally_arg)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/Variables.py'))
    return engine


@pytest.mark.parametrize(('is_argument'), [True, False, None])
@pytest.mark.parametrize(('is_attribute'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Variables(grepper, kind, consideration, is_attribute, is_argument):
    if any([consideration, is_attribute]):
        kind.reset()
        kind.Variables.is_attribute = is_attribute
        kind.Variables.is_argument = is_argument
        kind.Variables.consideration = consideration
        grepper.add_constraint(kind)
        results = all_results.copy()
        if is_attribute:
            results &= results_attributes
        elif is_attribute is False:
            results -= results_attributes
        if is_argument:
            results &= results_args
        elif is_argument is False:
            results -= results_args
        assert set(grepper.get_all_results()) == results


@pytest.mark.parametrize(('name', 'result'), [
    ('x', {(1, 4), (2, 10), (6, 19), (6, 22), (10, 6), (11, 15), (11, 23),
           (7, 19), (7, 16)}),
    ('y', {(4, 0), (10, 9), (11, 17), (11, 21)}),
    ('a', {(22, 0), (23, 6), (23, 22)}),
    ('test', {(23, 22), (15, 23), (16, 8), (16, 21), (19, 15)})
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Variables_name(grepper, kind, consideration, name, result):
    kind.reset()
    kind.Variables.name = name
    kind.Variables.consideration = consideration
    grepper.add_constraint(kind)
    assert set(grepper.get_all_results()) == results_formatter(result)


@pytest.mark.parametrize(('name', ('result')), [
    ('test', {(23, 22), (19, 15), (16, 8)})
])
def test_Variables_name_attr(grepper, kind, name, result):
    kind.reset()
    kind.Variables.is_attribute = True
    kind.Variables.name = name
    grepper.add_constraint(kind)
    assert set(grepper.get_all_results()) == results_formatter(result)
