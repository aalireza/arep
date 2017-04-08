import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Looping.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


results_for_else = results_formatter({
    (15, 0)
})

results_with_break = results_formatter({
    (21, 0), (22, 4), (27, 0), (34, 4)
})

results_infinite = results_formatter({
    (21, 0), (40, 4), (34, 4)
})

results_for = results_formatter({
    (1, 0), (15, 0), (2, 4), (8, 4), (11, 4), (13, 5), (22, 4)
})

results_while = results_formatter({
    (21, 0), (27, 0), (33, 0), (39, 0), (34, 4), (40, 4)
})

all_results = set(results_for | results_while)


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Looping.py'))
    return engine


def test_Looping(grepper):
    grepper.add_constraint(hg.Action.Looping())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('_for'), [True, False])
def test_from(grepper, _for):
    grepper.add_constraint(hg.Action.Looping(_for=_for))
    obtained_results = set(grepper.get_all_results())
    if _for:
        assert obtained_results == results_for
    else:
        assert obtained_results == (all_results - results_for)


@pytest.mark.parametrize(('_while'), [True, False])
def test_while(grepper, _while):
    grepper.add_constraint(hg.Action.Looping(_while=_while))
    obtained_results = set(grepper.get_all_results())
    if _while:
        assert obtained_results == results_while
    else:
        assert obtained_results == (all_results - results_while)


@pytest.mark.parametrize(('_for_else'), [True, False])
def test_for_else(grepper, _for_else):
    grepper.add_constraint(hg.Action.Looping(_for_else=_for_else))
    obtained_results = set(grepper.get_all_results())
    if _for_else:
        assert obtained_results == results_for_else
    else:
        assert obtained_results == (all_results - results_for_else)


@pytest.mark.parametrize(('_while'), [True, False, None])
@pytest.mark.parametrize(('_for'), [True, False, None])
@pytest.mark.parametrize(('_with_break'), [True, False])
def test_with_break(grepper, _with_break, _for, _while):
    grepper.add_constraint(hg.Action.Looping(_for=_for, _while=_while,
                                             _with_break=_with_break))
    obtained_results = set(grepper.get_all_results())
    if (_for is _while) and (_for is not None):
        target_result = set([])
    elif _with_break is True:
        target_result = results_with_break.copy()
    elif _with_break is None:
        target_result = all_results.copy()
    elif _with_break is False:
        target_result = (all_results - results_with_break)
    if (_for is True) or (_while is False):
        target_result -= results_while
    elif (_for is False) or (_while is True):
        target_result -= results_for
    assert obtained_results == target_result


@pytest.mark.parametrize(('_for'), [True, False, None])
@pytest.mark.parametrize(('_while'), [True, False, None])
@pytest.mark.parametrize(('infinite'), [True, False])
def test_non_terminating_test(grepper, _for, _while, infinite):
    grepper.add_constraint(hg.Action.Looping(
        _for=_for, _while=_while, _with_non_terminating_test=infinite))
    obtained_results = set(grepper.get_all_results())
    if (_for is _while) and (_for is not None):
        target_result = set([])
    elif infinite is True:
        target_result = results_infinite.copy()
    elif infinite is None:
        target_result = all_results.copy()
    elif infinite is False:
        target_result = (all_results - results_infinite)
    if (_for is True) or (_while is False):
        target_result -= results_while
    elif (_for is False) or (_while is True):
        target_result -= results_for
    assert obtained_results == target_result
