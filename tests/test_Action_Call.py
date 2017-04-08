import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Call.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


all_results = results_formatter({
    (4, 4), (5, 0), (6, 0), (15, 4), (6, 6), (9, 11), (9, 15)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Call.py'))
    return engine


def test_call(grepper):
    grepper.add_constraint(hg.Action.Call())
    assert set(grepper.get_all_results()) == all_results
