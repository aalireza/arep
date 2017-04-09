from higher_grep import core
from functools import partial

__constraint_modifier_localized = partial(
    core.constraint_template_modifier_func_maker, main='Location_Limit')


def Line_Numbers(starting_line=None, ending_line=None):
    return __constraint_modifier_localized(
        job='Line_Numbers', args=[
            ('minimum', starting_line), ('maximum', ending_line)
        ])


def Column_Numbers(starting_column=None, ending_column=None):
    return __constraint_modifier_localized(
        job='Column_Numbers', args=[
            ('minimum', starting_column), ('maximum', ending_column)
        ])
