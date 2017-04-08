import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Definition.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


all_results = results_formatter({
    (1, 0), (6, 0), (14, 0), (18, 0), (26, 0), (7, 4), (15, 4), (20, 4),
    (27, 4), (21, 8)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Definition.py'))
    return engine


def test_Definition(grepper):
    grepper.add_constraint(hg.Action.Definition())
    assert set(grepper.get_all_results()) == all_results
