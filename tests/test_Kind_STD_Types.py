from collections import namedtuple
import higher_grep as hg
import pytest
import os


results_template = namedtuple('STD_Types', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


all_results = results_formatter({
    (1, 6), (7, 8), (9, 7), (9, 18)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/STD_Types.py'))
    return engine


def test_STD_Types(grepper):
    grepper.add_constraint(hg.Kind.STD_Types())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('_type', 'result'), [
    (str, {(7, 8), (9, 18)}),
    (int, {(1, 6)}),
    (dict, set([])),
])
def test_type(grepper, _type, result):
    grepper.add_constraint(hg.Kind.STD_Types(_type=_type))
    assert set(grepper.get_all_results()) == results_formatter(result)
