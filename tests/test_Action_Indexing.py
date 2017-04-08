import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Indexing.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


all_results = results_formatter({
    (1, 4), (3, 5), (9, 7), (12, 10)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Indexing.py'))
    return engine


def test_Indexing(grepper):
    grepper.add_constraint(hg.Action.Indexing())
    assert set(grepper.get_all_results()) == all_results
