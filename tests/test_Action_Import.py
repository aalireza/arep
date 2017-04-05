from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Import', 'Line Column')

results = {results_template(x, y)
           for x, y in {(1, 0), (2, 0), (3, 0), (4, 0),
                        (10, 0), (15, 4)}}


@pytest.fixture(autouse=False)
def engine():
    instance = hg.Grepper(os.path.abspath('tests/data/Action/Import.py'))
    return instance

def test_import(engine):
    engine.add_constraints(hg.Action.Import())
    assert results == set(engine.get_all_results())

def test_import_without_from(engine):
    engine.add_constraints(hg.Action.Import(_from=False))
    assert set(engine.get_all_results) == {
        results_template(x, y)
        for x, y in {(1, 0), (4, 0), (10, 0), (15, 4)}}

@pytest.mark.parametrize(('_id', 'results'), [
    ('math', results_template(1,0)),
    ('Popen', results_template(2, 0)),
    ('sys', results_template(15, 4))
])
def test_import_id(engine, _id, results):
    engine.add_constraints(hg.Action.Import(_id=_id))
    print(engine.get_constraints())
    assert {results} == set(engine.get_all_results())

