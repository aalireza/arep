from ..utils import kind, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

augmented = results_formatter({
    (8, 0), (9, 0), (13, 0)
})

comparative = results_formatter({
    (15, 3)
})

unary = results_formatter({
    (11, 5)
})

binary = results_formatter({
    (1, 14), (3, 4), (5, 4), (6, 5), (1, 4), (1, 16), (1, 8), (1, 16)
})

boolean = results_formatter({
    (16, 10),
})

all_results = (augmented | comparative | unary | binary | boolean)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/Operations.py'))
    return engine


@pytest.mark.parametrize(('is_binary'), [True, False, None])
@pytest.mark.parametrize(('is_unary'), [True, False, None])
@pytest.mark.parametrize(('is_comparative'), [True, False, None])
@pytest.mark.parametrize(('is_boolean'), [True, False, None])
@pytest.mark.parametrize(('augments'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Operations(grepper, kind, consideration, augments, is_boolean,
                    is_comparative, is_unary, is_binary):
    if any([consideration, augments, is_boolean, is_comparative,
            is_unary, is_binary]):
        kind.reset()
        kind.Operations.augments_an_assignment = augments
        kind.Operations.is_boolean = is_boolean
        kind.Operations.is_comparative = is_comparative
        kind.Operations.is_unary = is_unary
        kind.Operations.is_binary = is_binary
        kind.Operations.consideration = consideration
        grepper.add_constraint(kind)
        results = all_results.copy()
        if augments:
            results &= augmented
        elif augments is False:
            results -= augmented
        if is_boolean:
            results &= boolean
        elif is_boolean is False:
            results -= boolean
        if is_comparative:
            results &= comparative
        elif is_comparative is False:
            results -= comparative
        if is_unary:
            results &= unary
        elif is_unary is False:
            results -= unary
        if is_binary:
            results &= binary
        elif is_binary is False:
            results -= binary
        assert set(grepper.get_all_results()) == results


@pytest.mark.parametrize(('symbol', 'results'), [
    ('+', {(1, 4), (9, 0)}),
    ('*', {(1, 8)}),
    ('**', {(1, 16), (3, 4)}),
    ('-', {(1, 14), (3, 4), (11, 5), (8, 0)}),
    ('/', {(1, 16), (5, 4)}),
    ('//', {(6, 5)}),
    ('%', {(13, 0)}),
    ('is', {(15, 3)}),
    ('and', {(16, 10)}),
    ('or', set([])),
    ('^', set([]))
])
def test_Operations_symbol(grepper, kind, symbol, results):
    kind.reset()
    kind.Operations.symbol = symbol
    grepper.add_constraint(kind)
    assert set(grepper.get_all_results()) == results_formatter(results)
