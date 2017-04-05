from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Call', 'Line Column')

results_with_msg = {results_template(2, 0), results_template(5, 4)}

results = {
    results_template(x, y)
    for x, y in {(1, 0), (2, 0), (5, 4)}
}


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Assertion.py'))
    return engine


def test_Assertion(grepper):
    grepper.add_constraint(hg.Action.Assertion())
    assert results == set(grepper.get_all_results())


@pytest.mark.parametrize(("is_sought"), [True, False])
def test_Assertion_with_error_msg(grepper, is_sought):
    grepper.add_constraint(hg.Action.Assertion(_with_error_msg=is_sought))
    if is_sought:
        assert set(grepper.get_all_results()) == results_with_msg
    else:
        assert set(grepper.get_all_results()) == (results - results_with_msg)
