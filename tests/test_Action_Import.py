from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Import', 'Line Column')

results_with_from = {results_template(x, y) for x, y in {(2, 0), (3, 0)}}

results_with_as = {results_template(x, y) for x, y in {(2, 0), (4, 0)}}

results = {
    results_template(x, y)
    for x, y in {(1, 0), (2, 0), (3, 0), (4, 0), (10, 0), (15, 4)}
}


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Import.py'))
    return engine


def test_import(grepper):
    grepper.add_constraint(hg.Action.Import())
    assert results == set(grepper.get_all_results())


@pytest.mark.parametrize(('_from_value'), [True, False])
def test_import_from(grepper, _from_value):
    grepper.add_constraint(hg.Action.Import(_from=_from_value))
    obtained_results = set(grepper.get_all_results())
    if _from_value:
        assert obtained_results == results_with_from
    else:
        assert obtained_results == (results - results_with_from)


@pytest.mark.parametrize(('_id', 'result'), [('math', results_template(
    1, 0)), ('Popen', results_template(2, 0)), ('sys', results_template(15,
                                                                        4))])
def test_import_id(grepper, _id, result):
    grepper.add_constraint(hg.Action.Import(_id=_id))
    assert {result} == set(grepper.get_all_results())


@pytest.mark.parametrize(('_from_id', 'result'), [
    ('subprocess', results_template(2, 0)),
    ('ast', results_template(3, 0)),
])
def test_from_id(grepper, _from_id, result):
    grepper.add_constraint(hg.Action.Import(_from=True, _from_id=_from_id))
    assert {result} == set(grepper.get_all_results())
