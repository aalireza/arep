from ..utils import kind, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

definitions = results_formatter({
    (14, 0), (29, 0), (30, 4)
})

calls = results_formatter({
    (25, 4), (26, 4)
})

all_results = (definitions | calls)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/Classes.py'))
    return engine


def test_Classes(grepper, kind):
    kind.reset()
    kind.Classes.consideration = True
    grepper.add_constraint(kind)
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('name', 'result'), [
    ('NotFunction', {(14, 0), (25, 4), (26, 4)}),
    ('SomeClass', {(29, 0)}),
    ('SomeOtherClass', {(30, 4)}),
    ('f', set([]))
])
def test_Classes_name(grepper, kind, name, result):
    kind.reset()
    kind.Classes.name = name
    grepper.add_constraint(kind)
    assert set(grepper.get_all_results()) == results_formatter(result)
