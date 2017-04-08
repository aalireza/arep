import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Continuing.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


all_results = results_formatter({
    (5, 8), (9, 8)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Continuing.py'))
    return engine


def test_Continuing(grepper):
    grepper.add_constraint(hg.Action.Continuing())
    assert set(grepper.get_all_results()) == all_results
