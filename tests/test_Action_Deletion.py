import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Deletion.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


all_results = results_formatter({
    (2, 0), (13, 12)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Deletion.py'))
    return engine


def test_Deletion(grepper):
    grepper.add_constraint(hg.Action.Deletion())
    assert set(grepper.get_all_results()) == all_results
