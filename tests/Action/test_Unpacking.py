from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

single = results_formatter({
    (3, 8), (11, 8), (15, 3)
})

double = results_formatter({
    (3, 17), (22, 8)
})

all_results = (single | double)


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Unpacking.py'))
    return engine


@pytest.mark.parametrize(('dim2'), [True, False, None])
@pytest.mark.parametrize(('dim1'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Unpacking(grepper, action, consideration, dim1, dim2):
    if any([consideration, dim1, dim2]):
        action.reset()
        action.Unpacking.one_dimensional = dim1
        action.Unpacking.two_dimensional = dim2
        action.Unpacking.consideration = consideration
        grepper.constraint_list.append(action)
        results = all_results.copy()
        if dim1:
            results &= single
        elif dim1 is False:
            results -= single
        if dim2:
            results &= double
        elif dim2 is False:
            results -= double
        assert set(grepper.all_results()) == results
