from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Trying', 'Line Column')

results_with_except_list = {
    results_template(x, y) for x, y in {
    }
}

results_with_finally = {results_template(x, y) for x, y in {(7, 0)}}

results = {
    results_template(x, y) for x, y in {(2, 0), (7, 0), (17, 4)}
}


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Trying.py'))
    return engine


def test_Trying(grepper):
    grepper.add_constraint(hg.Action.Trying())
    assert results == set(grepper.get_all_results())


@pytest.mark.parametrize(('_with_except_list', 'result'), [
    (IndexError, {results_template(2, 0), results_template(7, 0)}),
    ([IndexError, AttributeError], {results_template(7, 0)}),
    (AttributeError, {results_template(7, 0)}),
    (Exception, {results_template(17, 4)})
])
def test_with_except_list(grepper, _with_except_list, result):
    grepper.add_constraint(hg.Action.Trying(
        _with_except_list=_with_except_list))
    assert result == set(grepper.get_all_results())


@pytest.mark.parametrize(('_with_except_as_list', 'result'), [
    ('e', {results_template(7, 0)}),
    ('z', set([]))
])
def test_except_as_list(grepper, _with_except_as_list, result):
    grepper.add_constraint(hg.Action.Trying(
        _with_except_as_list=_with_except_as_list))
    assert result == set(grepper.get_all_results())


@pytest.mark.parametrize(('_with_finally', 'result'), [
    (True, {results_template(7, 0)}),
    (False, (results - {results_template(7, 0)}))
])
def test_with_finally(grepper, _with_finally, result):
    grepper.add_constraint(hg.Action.Trying(_with_finally=_with_finally))
    assert result == set(grepper.get_all_results())
