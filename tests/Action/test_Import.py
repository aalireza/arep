from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

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
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Import.py'))
    return engine


@pytest.mark.parametrize(('As'), [True, False, None])
@pytest.mark.parametrize(('From'), [True, False, None])
@pytest.mark.parametrize(('Import'), [True, False, None])
def test_Import(grepper, action, Import, From, As):
    action.reset()
    results = set()
    if any({Import, From, As}):
        action.Import.consideration = Import
        action.Import.From.consideration = From
        action.Import.As.consideration = As
        if Import is not False:
            results = all_results.copy()
        if From:
            results &= results_with_from
        elif From is False:
            results -= results_with_from
        if As:
            results &= results_with_as
        elif As is False:
            results -= results_with_as
        grepper.constraint_list.append(action)
        assert set(grepper.all_results()) == results


@pytest.mark.parametrize(('name', 'result'), [
    (None, all_results),
    ('math', {(1, 0)}),
    ('Popen', {(2, 0)}),
    ('sys', {(15, 4)})
])
def test_Import_name(grepper, action, name, result):
    action.reset()
    action.Import.name = name
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(result)


@pytest.mark.parametrize(('From_consideration'), [True, None])
@pytest.mark.parametrize(('From_name', 'results'), [
    (None, results_with_from),
    ('subprocess', {(2, 0)}),
    ('ast', {(3, 0)})
])
def test_Import_From(grepper, action, results, From_name, From_consideration):
    action.reset()
    action.Import.From.consideration = (
        True
        if (From_name is None) and (From_consideration) is None
        else From_consideration
    )
    action.Import.From.name = From_name
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(results)


@pytest.mark.parametrize(('As_name', 'results'), [
    ('popen', {(2, 0)}),
    ('math', {}),
    ('ast', {}),
    ('cpickle', {(4, 0)})
])
def test_Import_As_name(grepper, action, As_name, results):
    action.reset()
    action.Import.As.name = As_name
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(results)
