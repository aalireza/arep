from ..utils import kind, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

function_defs = results_formatter({
    (1, 0), (4, 0), (5, 4)
})

function_calls = results_formatter({
    (8, 15), (8, 17), (29, 16), (13, 9), (14, 4), (14, 11), (13, 31)
})

lambdas = results_formatter({
    (11, 4), (13, 13), (14, 11)
})

immediately_called_lambdas = results_formatter({
    (14, 11)
})

decorators = results_formatter({
    (23, 5)
})

builtins_calls = results_formatter({
    (13, 31), (13, 9), (14, 4), (23, 5)
})

all_results = (function_defs | function_calls | builtins_calls | lambdas |
               decorators)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/Functions.py'))
    return engine


@pytest.mark.parametrize(('decorator_consideration'), [True, False, None])
@pytest.mark.parametrize(('immediately_called'), [True, False, None])
@pytest.mark.parametrize(('lambda_consideration'), [True, False, None])
@pytest.mark.parametrize(('is_builtin'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Functions(grepper, kind, consideration, is_builtin,
                   lambda_consideration, immediately_called,
                   decorator_consideration):
    if any([consideration, is_builtin, lambda_consideration,
            immediately_called, decorator_consideration]):
        kind.reset()
        kind.Functions.is_builtin = is_builtin
        kind.Functions.Lambda.immediately_called = immediately_called
        kind.Functions.Decorators.consideration = decorator_consideration
        kind.Functions.Lambda.consideration = lambda_consideration
        kind.Functions.consideration = consideration
        grepper.add_constraint(kind)
        results = all_results.copy()
        if lambda_consideration:
            results &= lambdas
        elif lambda_consideration is False:
            results -= lambdas
        if is_builtin:
            results &= builtins_calls
        elif is_builtin is False:
            results -= builtins_calls
        if immediately_called:
            results &= immediately_called_lambdas
        elif immediately_called is False:
            results -= immediately_called_lambdas
        if decorator_consideration:
            results &= decorators
        elif decorator_consideration is False:
            results -= decorators
        assert set(grepper.get_all_results()) == results


@pytest.mark.parametrize(('name', 'results'), [
    ('f', {(1, 0), (5, 4), (8, 15), (29, 16)}),
    ('g', {(4, 0), (8, 17)}),
    ('l', {(11, 4)}),
    ('b', {}),
    ('print', {(14, 4)}),
    ('nonsense', {})
])
def test_Functions_name(grepper, kind, name, results):
    kind.reset()
    kind.Functions.name = name
    grepper.add_constraint(kind)
    assert set(grepper.get_all_results()) == results_formatter(results)


@pytest.mark.parametrize(('name', 'result'), [
    ('property', {(23, 5)}),
    ('not there', set([]))
])
@pytest.mark.parametrize(('is_builtin'), [True, False, None])
def test_Functions_Decorator_name(grepper, kind, name, result, is_builtin):
    kind.reset()
    kind.Functions.is_builtin = is_builtin
    kind.Functions.Decorators.name = name
    grepper.add_constraint(kind)
    if (
            is_builtin and bool(name != 'property') or
            bool(is_builtin is False) and bool(name == 'property')
    ):
        result = set([])
    assert set(grepper.get_all_results()) == results_formatter(result)
