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


# @pytest.mark.parametrize(('_with_elif'), [True, False])
# def test_with_elif(grepper, _with_elif):
#     grepper.add_constraint(hg.Action.Conditional(_with_elif=_with_elif))
#     if _with_elif:
#         assert set(grepper.get_all_results()) == results_with_elif
#     else:
#         assert set(grepper.get_all_results()) == (results - results_with_elif)


# @pytest.mark.parametrize(('_with_else'), [True, False])
# def test_with_else(grepper, _with_else):
#     grepper.add_constraint(hg.Action.Conditional(_with_else=_with_else))
#     if _with_else:
#         assert set(grepper.get_all_results()) == results_with_else
#     else:
#         assert set(grepper.get_all_results()) == (results - results_with_else)


# @pytest.mark.parametrize(('_is_ifexp'), [True, False])
# def test_is_ifexp(grepper, _is_ifexp):
#     grepper.add_constraint(hg.Action.Conditional(_is_ifexp=_is_ifexp))
#     if _is_ifexp:
#         assert set(grepper.get_all_results()) == results_is_ifexp
#     else:
#         assert set(grepper.get_all_results()) == (results - results_is_ifexp)


# @pytest.mark.parametrize(('_with_elif'), [True, False, None])
# @pytest.mark.parametrize(('_with_else'), [True, False, None])
# @pytest.mark.parametrize(('_is_ifexp'), [True, False, None])
# def test_combo(grepper, _with_elif, _with_else, _is_ifexp):
#     grepper.add_constraint(hg.Action.Conditional(
#         _with_elif=_with_elif, _with_else=_with_else, _is_ifexp=_is_ifexp))
#     obtained_results = set(grepper.get_all_results())
#     if _is_ifexp is None:
#         target_results = results.copy()
#     elif _is_ifexp is True:
#         target_results = results_is_ifexp.copy()
#     elif _is_ifexp is False:
#         target_results = (results - results_is_ifexp)
#     if _with_elif is True:
#         target_results &= results_with_elif
#     elif _with_elif is False:
#         target_results -= results_with_elif
#     if _with_else is True:
#         target_results &= results_with_else
#     elif _with_else is False:
#         target_results -= results_with_else
#     assert obtained_results == target_results
