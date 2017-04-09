from higher_grep import core
from functools import partial

__constraint_modifier_localized = partial(
    core.constraint_template_modifier_func_maker, main='Action')


def Call(should_consider=True):
    return __constraint_modifier_localized(
        job='Call', should_consider=should_consider)


def Initialization(should_consider=True):
    return __constraint_modifier_localized(
        job='Initialization', should_consider=should_consider)


def Import(_id=None, _from=None, _from_id=None, _as=None,
           should_consider=True):
    return __constraint_modifier_localized(
        job='Import', should_consider=should_consider, args=[
            ('id', _id), ('from', _from), ('from_id', _from_id),
            ('as', _as)
        ])


def Definition(should_consider=True):
    return __constraint_modifier_localized(
        job='Definition', should_consider=should_consider)


def Assignment(_with_op=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Assignment', should_consider=should_consider, args=[
            ('with_op', _with_op)
        ])


def Assertion(_with_error_msg=None, _error_msg_content=None,
              should_consider=True):
    return __constraint_modifier_localized(
        job='Assertion', should_consider=should_consider, args=[
            ('with_error_msg', _with_error_msg),
            ('error_msg_content', _error_msg_content)
        ])


def Looping(_for=None, _while=None, _for_else=None,
            _with_break=None, _with_non_terminating_test=None,
            should_consider=True,):
    return __constraint_modifier_localized(
        job='Looping', should_consider=should_consider, args=[
            ('for', _for), ('while', _while), ('for_else', _for_else),
            ('with_break', _with_break),
            ('with_non_terminating_test', _with_non_terminating_test)
        ])


def Conditional(_with_elif=None, _with_else=None, _is_ifexp=None,
                should_consider=True):
    return __constraint_modifier_localized(
        job='Conditional', should_consider=should_consider, args=[
            ('with_elif', _with_elif), ('with_else', _with_else),
            ('is_ifexp', _is_ifexp)
        ])


def With(_as=None, should_consider=True):
    return __constraint_modifier_localized(
        job="With", should_consider=should_consider, args=[('as', _as)])


def Deletion(should_consider=True):
    return __constraint_modifier_localized(
        job='Deletion', should_consider=should_consider)


def Indexing(should_consider=True):
    return __constraint_modifier_localized(
        job='Indexing', should_consider=should_consider)


def Trying(_with_except_list=None, _with_except_as_list=None,
           _with_finally=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Trying', should_consider=should_consider, args=[
            ('with_except_list', _with_except_list),
            ('with_except_as_list', _with_except_as_list),
            ('with_finally', _with_finally)
        ])


def Raising(_error_type=None, _error_message=None, _cause=None,
            should_consider=True):
    return __constraint_modifier_localized(
        job='Raising', should_consider=should_consider, args=[
            ('error_type', _error_type),
            ('error_message', _error_message),
            ('cause', _cause)
        ])


def Yielding(_yield_from=None, _in_comprehension=None,
             should_consider=True):
    return __constraint_modifier_localized(
        job='Yielding', should_consider=should_consider, args=[
            ('in_comprehension', _in_comprehension),
            ('yield_from', _yield_from)
        ])


def Making_Global(_id=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Making_Global', should_consider=should_consider, args=[
            ('id', _id)
        ])


def Making_Nonlocal(_id=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Making_Nonlocal', should_consider=should_consider, args=[
            ('id', _id)
        ])


def Passing(should_consider=True):
    return __constraint_modifier_localized(
        job='Passing', should_consider=should_consider)


def Returning(should_consider=True):
    return __constraint_modifier_localized(
        job='Returning', should_consider=should_consider)


def Breaking(should_consider=True):
    return __constraint_modifier_localized(
        job='Breaking', should_consider=should_consider)


def Continuing(should_consider=True):
    return __constraint_modifier_localized(
        job='Continuing', should_consider=should_consider)
