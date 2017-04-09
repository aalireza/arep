from ..utils import results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_regular = results_formatter({
    (4, 0), (7, 0), (22, 0), (6, 0)
})

results_temp = results_formatter({
    (1, 4), (2, 10)
})

results_args = results_formatter({
    (6, 19), (6, 22), (7, 16), (7, 19), (16, 21), (15, 23), (10, 6), (10, 9),
    (11, 15), (11, 17), (11, 21), (11, 23)
})

results_attributes = results_formatter({
    (16, 8), (19, 15), (23, 22)
})

all_results = (results_regular | results_temp | results_args |
               results_attributes)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/Variables.py'))
    return engine


# def test_Variables(grepper):
#     grepper.add_constraint(hg.Kind.Variables())
#     assert set(grepper.get_all_results()) == all_results


# @pytest.mark.parametrize(('_type', 'result'), [
#     (str, {(7, 8), (9, 18)}),
#     (int, {(1, 6)}),
#     (dict, set([])),
# ])
# def test_type(grepper, _type, result):
#     grepper.add_constraint(hg.Kind.STD_Types(_type=_type))
#     assert set(grepper.get_all_results()) == results_formatter(result)
