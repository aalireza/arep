import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Import.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


results_with_from = results_formatter({
    (2, 0), (3, 0)
})

results_with_as = results_formatter({
    (2, 0), (4, 0)
})

all_results = results_formatter({
    (1, 0), (2, 0), (3, 0), (4, 0), (10, 0), (15, 4)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Import.py'))
    return engine


def test_import(grepper):
    grepper.add_constraint(hg.Action.Import())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('_from_value'), [True, False])
def test_import_from(grepper, _from_value):
    grepper.add_constraint(hg.Action.Import(_from=_from_value))
    obtained_results = set(grepper.get_all_results())
    if _from_value:
        assert obtained_results == results_with_from
    else:
        assert obtained_results == (all_results - results_with_from)


@pytest.mark.parametrize(('_id', 'result'), [
    ('math', {(1, 0)}),
    ('Popen', {(2, 0)}),
    ('sys', {(15, 4)})
])
def test_import_id(grepper, _id, result):
    grepper.add_constraint(hg.Action.Import(_id=_id))
    assert set(grepper.get_all_results()) == results_formatter(result)


@pytest.mark.parametrize(('_from_id', 'result'), [
    ('subprocess', {(2, 0)}),
    ('ast', {(3, 0)}),
])
def test_from_id(grepper, _from_id, result):
    grepper.add_constraint(hg.Action.Import(_from=True, _from_id=_from_id))
    assert set(grepper.get_all_results()) == results_formatter(result)
