from collections import namedtuple
import higher_grep as hg
import pytest
import os


results_template = namedtuple('Assertion', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


results_with_msg = results_formatter({(2, 0), (5, 4)})
all_results = results_formatter({(1, 0), (2, 0), (5, 4)})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Assertion.py'))
    return engine


def test_Assertion(grepper):
    grepper.add_constraint(hg.Action.Assertion())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(("is_sought"), [True, False])
def test_Assertion_with_error_msg(grepper, is_sought):
    grepper.add_constraint(hg.Action.Assertion(_with_error_msg=is_sought))
    if is_sought:
        assert set(grepper.get_all_results()) == results_with_msg
    else:
        assert set(grepper.get_all_results()) == (
            all_results - results_with_msg
        )
