from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Conditional', 'Line Column')

results_with_elif = {
    results_template(x, y) for x, y in {
        (2, 0), (13, 0)
    }
}

results_with_else = {
    results_template(x, y) for x, y in {
        (2, 0), (11, 5)
    }
}

results_is_ifexp = {
    results_template(x, y) for x, y in {
        (11, 5)
    }
}

results_in_comprehensions = {
    results_template(x, y) for x, y in {
        (18, 10), (20, 11), (23, 4), (23, 16)
    }
}

results = ({results_template(30, 4)} | results_with_elif | results_with_else |
           results_is_ifexp | results_in_comprehensions)


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Conditional.py'))
    return engine


def test_Conditional(grepper):
    grepper.add_constraint(hg.Action.Conditional())
    print(results)
    assert results == set(grepper.get_all_results())


@pytest.mark.parametrize(('_with_elif'), [True, False])
def test_with_elif(grepper, _with_elif):
    grepper.add_constraint(hg.Action.Conditional(_with_elif=_with_elif))
    if _with_elif:
        assert set(grepper.get_all_results()) == results_with_elif
    else:
        assert set(grepper.get_all_results()) == (results - results_with_elif)


@pytest.mark.parametrize(('_with_else'), [True, False])
def test_with_else(grepper, _with_else):
    grepper.add_constraint(hg.Action.Conditional(_with_else=_with_else))
    if _with_else:
        assert set(grepper.get_all_results()) == results_with_else
    else:
        assert set(grepper.get_all_results()) == (results - results_with_else)


@pytest.mark.parametrize(('_is_ifexp'), [True, False])
def test_is_ifexp(grepper, _is_ifexp):
    grepper.add_constraint(hg.Action.Conditional(_is_ifexp=_is_ifexp))
    if _is_ifexp:
        assert set(grepper.get_all_results()) == results_is_ifexp
    else:
        assert set(grepper.get_all_results()) == (results - results_is_ifexp)


@pytest.mark.parametrize(('_with_elif'), [True, False, None])
@pytest.mark.parametrize(('_with_else'), [True, False, None])
@pytest.mark.parametrize(('_is_ifexp'), [True, False, None])
def test_combo(grepper, _with_elif, _with_else, _is_ifexp):
    grepper.add_constraint(hg.Action.Conditional(
        _with_elif=_with_elif, _with_else=_with_else, _is_ifexp=_is_ifexp))
    obtained_results = set(grepper.get_all_results())
    if _is_ifexp is None:
        target_results = results.copy()
    elif _is_ifexp is True:
        target_results = results_is_ifexp.copy()
    elif _is_ifexp is False:
        target_results = (results - results_is_ifexp)
    if _with_elif is True:
        target_results &= results_with_elif
    elif _with_elif is False:
        target_results -= results_with_elif
    if _with_else is True:
        target_results &= results_with_else
    elif _with_else is False:
        target_results -= results_with_else
    assert obtained_results == target_results