from higher_grep import core
from functools import partial

__constraint_modifier_localized = partial(
    core.constraint_template_modifier_func_maker, main='Kind')


def Variables(_id=None, _is_attribute=None, _is_argument=None,
              should_consider=True):
    return __constraint_modifier_localized(
        job='Variables', should_consider=should_consider, args=[
            ('id', _id), ('is_attribute', _is_attribute),
            ('is_argument', _is_argument),
        ])


def STD_Types(_type=None, should_consider=True):
    return __constraint_modifier_localized(
        job='STD_Types', should_consider=should_consider, args=[
            ('type', _type)
        ])


def Functions(_id=None, _is_lambda=None, _is_decorator=None,
              should_consider=True):
    return __constraint_modifier_localized(
        job='Functions', should_consider=should_consider, args=[
            ('id', _id), ('is_lambda', _is_lambda),
            ('is_decorator', _is_decorator)
        ])


def Decorators(_id=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Decorators', should_consider=should_consider, args=[
            ('id', _id)
        ])


def Classes(_id=None, _superclass_type=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Classes', should_consider=should_consider, args=[
            ('id', _id), ('superclass_type', _superclass_type)
        ])


def Attributes(_id=None, _class_id=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Generators', should_consider=should_consider, args=[
            ('id', _id), ('class_id', _class_id)
        ])


def Methods(_id=None, _class_id=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Methods', should_consider=should_consider, args=[
            ('id', _id), ('class_id', _class_id)
        ])


def Generators(_id=None, should_consider=True):
    return __constraint_modifier_localized(
        job='Generators', should_consider=should_consider, args=[
            ('id', _id)
        ])


def Comprehensions(_of_list=None, _of_dict=None, _of_gen=None,
                   should_consider=True):
    return __constraint_modifier_localized(
        job='Comprehensions', should_consider=should_consider, args=[
            ('of_list', _of_list), ('of_dict', _of_dict),
            ('of_gen', _of_gen)
        ])


def Operations(_operation_str=None, _is_unary=None, _is_binary=None,
               should_consider=True):
    return __constraint_modifier_localized(
        job='Operations', should_consider=should_consider, args=[
            ('operation_str', _operation_str), ('is_unary', _is_unary),
            ('is_binary', _is_binary)
        ])
