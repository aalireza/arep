from ..utils import properties, results_formatter, coordinate_of_all_nodes
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))


@pytest.fixture
def program_path():
    return os.path.abspath('tests/data/Properties/Positional.py')


@pytest.fixture
def grepper(program_path):
    engine = arep.Grepper(program_path)
    return engine


@pytest.fixture
def coordinates(program_path):
    with open(program_path, 'r') as program:
        return results_formatter(coordinate_of_all_nodes(program.read()))


@pytest.mark.parametrize(('col_max'), [None, 0, 1, 5, 24, 28])
@pytest.mark.parametrize(('col_min'), [None, 0, 1, 10, 20, 28])
@pytest.mark.parametrize(('line_max'), [None, 1, 5, 10, 16])
@pytest.mark.parametrize(('line_min'), [None, 1, 2, 10])
def test_Positional(grepper, coordinates, properties, line_min, line_max,
                    col_min, col_max):
    if any([line_min, line_max, col_min, col_max]):
        properties.reset()
        properties.Positional.Line_Numbers.minimum = line_min
        properties.Positional.Line_Numbers.maximum = line_max
        properties.Positional.Column_Numbers.minimum = col_min
        properties.Positional.Column_Numbers.maximum = col_max
        grepper.constraint_list.append(properties)
        filter_funcs = set([])
        if line_min is not None:
            filter_funcs.add((lambda result: line_min <= result.line))
        if line_max is not None:
            filter_funcs.add((lambda result: result.line <= line_max))
        if col_min is not None:
            filter_funcs.add((lambda result: col_min <= result.column))
        if col_max is not None:
            filter_funcs.add((lambda result: result.column <= col_max))
        results = set(filter(
            lambda result: all([f(result) for f in filter_funcs]),
            coordinates
        ))
        assert set(grepper.all_results()) == results
