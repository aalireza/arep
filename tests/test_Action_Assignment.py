from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Assignment', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


aug_assign_results = results_formatter({
    (9, 4)
})

all_results = results_formatter({
    (5, 0), (11, 0), (12, 0), (16, 0), (18, 0), (2, 4), (8, 4), (9, 4)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Assignment.py'))
    return engine


def test_Assignment(grepper):
    grepper.add_constraint(hg.Action.Assignment())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('aug_status'), [True, False])
def test_Assignment_aug(grepper, aug_status):
    grepper.add_constraint(hg.Action.Assignment(_with_op=aug_status))
    if aug_status:
        assert set(grepper.get_all_results()) == aug_assign_results
    else:
        assert set(grepper.get_all_results()) == (
            all_results - aug_assign_results
        )
