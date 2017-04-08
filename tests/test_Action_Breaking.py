import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Breaking.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


all_results = results_formatter({
    (2, 4), (6, 8), (15, 12)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Breaking.py'))
    return engine


def test_Breaking(grepper):
    grepper.add_constraint(hg.Action.Breaking())
    assert set(grepper.get_all_results()) == all_results
