import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Returning.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


results_in_lambda = results_formatter(set([]))

results_regular = results_formatter({
    (2, 4), (6, 8)
})

all_results = (results_regular | results_in_lambda)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Returning.py'))
    return engine


def test_Returning(grepper):
    grepper.add_constraint(hg.Action.Returning())
    assert set(grepper.get_all_results()) == all_results
