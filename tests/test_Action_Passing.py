import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Passing.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


all_results = results_formatter({
    (2, 4), (10, 8)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Passing.py'))
    return engine


def test_Passing(grepper):
    grepper.add_constraint(hg.Action.Passing())
    assert all_results == set(grepper.get_all_results())
