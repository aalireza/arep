from ..utils import kind, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

list_comp = results_formatter({
    (2, 14)
})

dict_comp = results_formatter({
    (6, 11)
})

set_comp = results_formatter({
    (15, 34)
})

gen_expr = results_formatter({
    (15, 5), (13, 5)
})

all_results = (list_comp | dict_comp | set_comp | gen_expr)


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Kind/Comprehensions.py'))
    return engine


@pytest.mark.parametrize(('of_gen'), [True, False, None])
@pytest.mark.parametrize(('of_set'), [True, False, None])
@pytest.mark.parametrize(('of_dict'), [True, False, None])
@pytest.mark.parametrize(('of_list'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Comprehensions(grepper, kind, consideration, of_gen, of_set, of_dict,
                        of_list):
    if any([consideration, of_gen, of_set, of_dict, of_list]):
        kind.reset()
        kind.Comprehensions.of_dict = of_dict
        kind.Comprehensions.of_list = of_list
        kind.Comprehensions.of_set = of_set
        kind.Comprehensions.of_gen = of_gen
        kind.Comprehensions.consideration = consideration
        grepper.constraint_list.append(kind)
        results = all_results.copy()
        if of_list:
            results &= list_comp
        elif of_list is False:
            results -= list_comp
        if of_dict:
            results &= dict_comp
        elif of_dict is False:
            results -= dict_comp
        if of_set:
            results &= set_comp
        elif of_set is False:
            results -= set_comp
        if of_gen:
            results &= gen_expr
        elif of_gen is False:
            results -= gen_expr
        assert set(grepper.all_results()) == results
