from ..utils import kind, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

function_defs = results_formatter({
    (1, 0), (4, 0), (5, 4), (32, 0), (36, 0), (37, 4)
})

function_calls = results_formatter({
    (8, 15), (8, 17), (29, 16), (13, 9), (14, 4), (14, 11), (13, 31), (38, 15),
    (38, 27), (39, 11), (39, 24), (39, 38)
})

lambdas = results_formatter({
    (11, 4), (13, 13), (14, 11), (33, 12), (39, 24)
})

immediately_called_lambdas = results_formatter({
    (14, 11), (39, 24)
})

decorators = results_formatter({
    (23, 5)
})

builtins_calls = results_formatter({
    (13, 31), (13, 9), (14, 4), (23, 5), (38, 15), (38, 27), (39, 11), (39, 38)
})

without_parameters = results_formatter({
    (32, 0), (33, 12), (23, 5)
})

without_args = (without_parameters | results_formatter({
    (29, 16)
}))

with_kwargs = results_formatter({
    (1, 0), (29, 16), (37, 4)
})

variadic_args = results_formatter({
    (36, 0), (37, 4), (39, 24)
})

variadic_kwargs = results_formatter({
    (37, 4)
})

with_default_values = results_formatter({
    (1, 0)
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

@pytest.mark.parametrize(('default'), [True, False, None])
@pytest.mark.parametrize(('kwargs_variadicity'), [True, False, None])
@pytest.mark.parametrize(('kwargs'), [True, False, None])
@pytest.mark.parametrize(('args_variadicity'), [True, False, None])
@pytest.mark.parametrize(('args'), [True, False, None])
@pytest.mark.parametrize(('parameter_consideration'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Functions_Parameters(grepper, kind, consideration, default,
                              args, args_variadicity,
                              kwargs, kwargs_variadicity,
                              parameter_consideration):
    if any([consideration, parameter_consideration, default,
            args, args_variadicity, kwargs, kwargs_variadicity]):
        kind.reset()
        kind.Functions.Parameters.with_default_values = default
        kind.Functions.Parameters.Arguments.is_variadic = args_variadicity
        kind.Functions.Parameters.Arguments.consideration = args
        kind.Functions.Parameters.Keywords.is_variadic = kwargs_variadicity
        kind.Functions.Parameters.Keywords.consideration = kwargs
        kind.Functions.Parameters.consideration = parameter_consideration
        kind.Functions.consideration = consideration
        results = all_results.copy()
        if parameter_consideration:
            results -= without_parameters
        elif parameter_consideration is False:
            results &= without_parameters
        if args:
            results -= without_args
        elif args is False:
            results &= without_args
        if args_variadicity:
            results &= variadic_args
        elif args_variadicity is False:
            results -= variadic_args
        if kwargs:
            results &= with_kwargs
        elif kwargs is False:
            results -= with_kwargs
        if kwargs_variadicity:
            results &= variadic_kwargs
        elif kwargs_variadicity is False:
            results -= variadic_kwargs
        if default:
            results &= with_default_values
        elif default is False:
            results -= with_default_values
        grepper.add_constraint(kind)
        assert set(grepper.get_all_results()) == results_formatter(results)
