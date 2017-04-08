from collections import namedtuple
import higher_grep as hg
import pytest
import os


results_template = namedtuple('STD_Types', 'Line Column')
all_results = {(1, 6), (7, 8), (9, 7), (9, 18)}


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/STD_Types.py'))
    return engine


def test_STD_Types(grepper):
    grepper.add_constraint(hg.Kind.STD_Types())
    assert results_formatter(all_results) == set(grepper.get_all_results())


@pytest.mark.parametrize(('_type', 'results'), [
    (str, {(7, 8), (9, 18)}),
    (int, {(1, 6)}),
    (dict, set([])),
])
def test_type(grepper, _type, results):
    grepper.add_constraint(hg.Kind.STD_Types(_type=_type))
    assert results_formatter(results) == set(grepper.get_all_results())
