from higher_grep.utils import Result
from higher_grep.constraints import Action, Kind, Properties
import pytest


def results_formatter(coordinates, name):
    results = set([])
    for result in coordinates:
        if type(result) is Result:
            results.add(result)
        else:
            results.add(Result(
                # Removing `test_` from `test_something.py`
                '_'.join(name.split('_')[1:]), result[0], result[1]
            ))
    return results


@pytest.fixture
def action():
    instance = Action()
    return instance


@pytest.fixture
def kind():
    instance = Kind()
    return instance


@pytest.fixture
def properties():
    instance = Properties()
    return instance