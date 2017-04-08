from __future__ import absolute_import, division, print_function
from collections import namedtuple, defaultdict
from functools import partial
from inspect import getfullargspec as spec
import ast
import os
import sys

if sys.version_info > (3, 0):
    long = int


def _Constraints_template():
    return {
        'Action': {
            'Call': {
                'should_consider': None,
            },
            'Initialization': {
                'should_consider': None,
            },
            'Import': {
                'should_consider': None,
                'id': None,
                'from': None,
                'from_id': None,
                'as': None,
            },
            'Definition': {
                'should_consider': None,
            },
            'Assignment': {
                'should_consider': None,
                'with_op': None,
            },
            'Assertion': {
                'should_consider': None,
                'with_error_msg': None,
                'error_msg_content': None,
            },
            'Looping': {
                'should_consider': None,
                'for': None,
                'while': None,
                'for_else': None,
                'with_break': None,
                'with_non_terminating_test': None,
            },
            'Conditional': {
                'should_consider': None,
                'with_elif': None,
                'with_else': None,
                'is_ifexp': None,
            },
            'With': {
                'should_consider': None,
                'as': None,
            },
            'Deletion': {
                'should_consider': None,
            },
            'Indexing': {
                'should_consider': None,
            },
            'Trying': {
                'should_consider': None,
                'with_except_list': None,
                'with_except_as_list': None,
                'with_finally': None,
            },
            'Raising': {
                'should_consider': None,
                'error_type': None,
                'error_message': None,
                'cause': None,
            },
            'Yielding': {
                'should_consider': None,
                'in_comprehension': None,
                'yield_from': None,
            },
            'Making_Global': {
                'should_consider': None,
                'id': None,
            },
            'Making_Nonlocal': {
                'should_consider': None,
                'id': None,
            },
            'Passing': {
                'should_consider': None,
            },
            'Returning': {
                'should_consider': None,
            },
            'Breaking': {
                'should_consider': None,
            },
            'Continuing': {
                'should_consider': None,
            },
        },
        'Kind': {
            'Variables': {
                'should_consider': None,
                'id': None,
                'is_attribute': None,
            },
            'STD_Types': {
                'should_consider': None,
                'type': None,
            },
            'Functions': {
                'should_consider': None,
                'id': None,
                'is_lambda': None,
                'is_decorator': None,
            },
            'Decorators': {
                'should_consider': None,
                'id': None,
            },
            'Classes': {
                'should_consider': None,
                'id': None,
                'superclass_type': None,
            },
            'Attributes': {
                'should_consider': None,
                'id': None,
                'class_id': None,
            },
            'Methods': {
                'should_consider': None,
                'id': None,
                'class_id': None,
            },
            'Generators': {
                'should_consider': None,
                'id': None,
            },
            'Comprehensions': {
                'should_consider': None,
                'of_list': None,
                'of_dict': None,
                'of_gen': None,
            },
            'Operations': {
                'should_consider': None,
                'operation_str': None,
                'is_unary': None,
                'is_binary': None,
            },
        },
        'Location_Limit': {
            'Line_Numbers': {
                'minimum': None,
                'maximum': None,
            },
            'Column_Numbers': {
                'minimum': None,
                'maximum': None,
            }
        }
    }


def _establish_parent_link(tree):
    to_be_processed = [tree]
    while to_be_processed:
        try:
            current_parent = to_be_processed.pop(0)
            children = current_parent.body
            for child in children:
                child._parent = current_parent
            to_be_processed.extend(children)
        except AttributeError:
            if to_be_processed:
                to_be_processed.pop(0)
        except IndexError:
            continue
    if not to_be_processed:
        return tree
    raise Exception


def count_arity(func):
    if any(
            [possibly_infinite is not None
             for possibly_infinite in {spec(func).varargs, spec(func).varkw}]
    ):
        return float("inf")
    return len(spec(func).args)


def _ast_mapped_operators():

    def basic_reducer(*args, definition=(lambda *args: None)):
        results = set([])
        current_element = args[0]
        if count_arity(definition) == 1:
            assert len(args) == 1
            results.add(definition(current_element))
        else:
            assert len(args) > 1
            for other_element in args[1:]:
                results.add(definition(current_element, other_element))
                current_element = other_element
        return all(results)

    ast_mappings = dict()

    equality_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x == y)
    )
    ast_mappings[ast.Eq.__name__] = equality_definition_checker

    inequality_definition_checker = (
        lambda *args: not equality_definition_checker(*args)
    )
    ast_mappings[ast.NotEq.__name__] = inequality_definition_checker

    less_than_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x < y)
    )
    ast_mappings[ast.Lt.__name__] = less_than_definition_checker

    less_than_or_equal_definition_checker = (
        lambda *args: (less_than_definition_checker(*args) or
                       equality_definition_checker(*args))
    )
    ast_mappings[ast.LtE.__name__] = less_than_or_equal_definition_checker

    greater_than_or_equal_definition_checker = (
        lambda *args: not less_than_definition_checker(*args)
    )
    ast_mappings[ast.GtE.__name__] = greater_than_or_equal_definition_checker

    greater_than_definition_checker = (
        lambda *args: not less_than_or_equal_definition_checker(*args)
    )
    ast_mappings[ast.GtE.__name__] = greater_than_definition_checker

    is_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: bool(x is y)))
    ast_mappings[ast.Is.__name__] = is_definition_checker

    is_not_definition_checker = (
        lambda *args: not is_definition_checker(*args)
    )
    ast_mappings[ast.IsNot.__name__] = is_not_definition_checker

    in_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: bool(x in y))
    )
    ast_mappings[ast.In.__name__] = in_definition_checker

    not_in_definition_checker = (
        lambda *args: not in_definition_checker(*args)
    )
    ast_mappings[ast.NotIn.__name__] = not_in_definition_checker

    additive_identity_definition_checker = partial(
        basic_reducer, definition=(lambda x: +x)
    )
    ast_mappings[ast.UAdd.__name__] = additive_identity_definition_checker

    additive_inverse_definition_checker = partial(
        basic_reducer, definition=(lambda x: -x)
    )
    ast_mappings[ast.USub.__name__] = additive_inverse_definition_checker

    addition_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x + y)
    )
    ast_mappings[ast.Add.__name__] = addition_definition_checker

    subtraction_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x - y)
    )
    ast_mappings[ast.Sub.__name__] = subtraction_definition_checker

    multiplication_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x * y)
    )
    ast_mappings[ast.Mult.__name__] = multiplication_definition_checker

    division_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x / y)
    )
    ast_mappings[ast.Div.__name__] = division_definition_checker

    integer_division_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x // y)
    )
    ast_mappings[ast.FloorDiv.__name__] = integer_division_definition_checker

    modulo_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x % y)
    )
    ast_mappings[ast.Mod.__name__] = modulo_definition_checker

    exponentiation_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x ** y)
    )
    ast_mappings[ast.Pow.__name__] = exponentiation_definition_checker

    matrix_multiplication_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x @ y)
    )
    ast_mappings[
        ast.MatMult.__name__] = matrix_multiplication_definition_checker

    boolean_not_definition_checker = partial(
        basic_reducer, definition=(lambda x: not x)
    )
    ast_mappings[ast.Not.__name__] = boolean_not_definition_checker

    boolean_and_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x and y)
    )
    ast_mappings[ast.And.__name__] = boolean_and_definition_checker

    boolean_or_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x or y)
    )
    ast_mappings[ast.Or.__name__] = boolean_or_definition_checker

    bitwise_inversion_definition_checker = partial(
        basic_reducer, definition=(lambda x: ~x)
    )
    ast_mappings[ast.Invert.__name__] = bitwise_inversion_definition_checker

    bitwise_left_shift_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x << y)
    )
    ast_mappings[ast.LShift.__name__] = bitwise_left_shift_definition_checker

    bitwise_right_shift_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x >> y)
    )
    ast_mappings[ast.RShift.__name__] = bitwise_right_shift_definition_checker

    bitwise_and_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x & y)
    )
    ast_mappings[ast.BitAnd.__name__] = bitwise_and_definition_checker

    bitwise_or_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x | y)
    )
    ast_mappings[ast.BitOr.__name__] = bitwise_or_definition_checker

    bitwise_xor_definition_checker = partial(
        basic_reducer, definition=(lambda x, y: x ^ y)
    )
    ast_mappings[ast.BitXor.__name__] = bitwise_xor_definition_checker

    return ast_mappings


def _Knowledge_template():
    _knowledge = {
        'comprehension_forms': {
            ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp
        },
        'builtin_kinds': {
            'numbers': {
                int, float, long, complex
            },
            'collections': {
                dict, set, frozenset, list, bytearray
            },
            'data': {
                type, bytes, bytearray, memoryview
            },
            'slices': {
                str, list, bytearray, bytes
            },
            'text': {
                str
            },
            'logic': {
                bool
            }
        }
    }
    _knowledge['builtin_types'] = {
        builtin_type
        for builtin_kind_set in _knowledge['builtin_kinds'].values()
        for builtin_type in builtin_kind_set
    }
    return _knowledge


def _update_knowledge_template(
        ast_tree_with_parent_pointers, knowledge_template, results_name,
        _with_classes=True, _with_funcs=True):
    def func_name_checker(node):
        if type(node) is ast.FunctionDef:
            return ('Function', node.name)
        elif type(node) is ast.Lambda:
            if type(node._parent) is ast.Call:
                return ('Function', ast.Lambda)
        return False

    def class_name_checker(node):
        if type(node) is ast.ClassDef:
            return ('Class', node.name)
        return False

    name_kinds = {
        'Function': defaultdict(list),
        'Class': defaultdict(list),
    }
    name_checkers = set([])
    if _with_funcs:
        name_checkers.add(func_name_checker)
    if _with_classes:
        name_checkers.add(class_name_checker)
    for node in ast.walk(ast_tree_with_parent_pointers):
        for name_checker in name_checkers:
            try:
                result = name_checker(node)
                if result:
                    name_kinds[result[0]][result[1]].append(
                        _Result(
                            name=results_name,
                            line_number=node.lineno,
                            column_number=node.col_offset
                        )
                    )
            except AttributeError:
                pass

    for name_kind, names_set in name_kinds.items():
        if len(names_set):
            knowledge_template[name_kind] = names_set
    return knowledge_template


def _comparison_evaluator(node):

    def type_seive(comparator):
        if bool(type(comparator) is ast.Num):
            return comparator.n
        elif bool(type(comparator) is ast.Str):
            return comparator.s
        raise NotImplementedError(
            "Comparator can't be {}".format(type(comparator))
        )

    if not bool(type(node) is ast.Compare):
        raise TypeError("{} is not a comparator".format(node))
    operations = _ast_mapped_operators()
    left = type_seive(node.left)
    for op in map(
            lambda op: operations[type(op).__name__],
            node.ops
    ):
        current_comparator = type_seive(node.comparators.pop(0))
        left = op(left, current_comparator)

    return left


def _constraint_template_modifier_func_maker(main,
                                             job,
                                             should_consider=None,
                                             args=None):
    def constraint_template_modifier(template):
        if should_consider is not None:
            template[main][job]['should_consider'] = should_consider
        if args is not None:
            for key, value in args:
                template[main][job][key] = value

    return constraint_template_modifier


class Action(object):
    _constraint_modifier_localized = partial(
        _constraint_template_modifier_func_maker, main='Action')

    def Call(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Call', should_consider=should_consider)

    def Initialization(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Initialization', should_consider=should_consider)

    def Import(_id=None, _from=None, _from_id=None, _as=None,
               should_consider=True):
        return Action._constraint_modifier_localized(
            job='Import', should_consider=should_consider, args=[
                ('id', _id), ('from', _from), ('from_id', _from_id),
                ('as', _as)
            ])

    def Definition(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Definition', should_consider=should_consider)

    def Assignment(_with_op=None, should_consider=True):
        return Action._constraint_modifier_localized(
            job='Assignment', should_consider=should_consider, args=[
                ('with_op', _with_op)
            ])

    def Assertion(_with_error_msg=None, _error_msg_content=None,
                  should_consider=True):
        return Action._constraint_modifier_localized(
            job='Assertion', should_consider=should_consider, args=[
                ('with_error_msg', _with_error_msg),
                ('error_msg_content', _error_msg_content)
            ])

    def Looping(_for=None, _while=None, _for_else=None,
                _with_break=None, _with_non_terminating_test=None,
                should_consider=True,):
        return Action._constraint_modifier_localized(
            job='Looping', should_consider=should_consider, args=[
                ('for', _for), ('while', _while), ('for_else', _for_else),
                ('with_break', _with_break),
                ('with_non_terminating_test', _with_non_terminating_test)
            ])

    def Conditional(_with_elif=None, _with_else=None, _is_ifexp=None,
                    should_consider=True):
        return Action._constraint_modifier_localized(
            job='Conditional', should_consider=should_consider, args=[
                ('with_elif', _with_elif), ('with_else', _with_else),
                ('is_ifexp', _is_ifexp)
            ])

    def With(_as=None, should_consider=True):
        return Action._constraint_modifier_localized(
            job="With", should_consider=should_consider, args=[('as', _as)])

    def Deletion(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Deletion', should_consider=should_consider)

    def Indexing(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Indexing', should_consider=should_consider)

    def Trying(_with_except_list=None, _with_except_as_list=None,
               _with_finally=None, should_consider=True):
        return Action._constraint_modifier_localized(
            job='Trying', should_consider=should_consider, args=[
                ('with_except_list', _with_except_list),
                ('with_except_as_list', _with_except_as_list),
                ('with_finally', _with_finally)
            ])

    def Raising(_error_type=None, _error_message=None, _cause=None,
                should_consider=True):
        return Action._constraint_modifier_localized(
            job='Raising', should_consider=should_consider, args=[
                ('error_type', _error_type),
                ('error_message', _error_message),
                ('cause', _cause)
            ])

    def Yielding(_yield_from=None, _in_comprehension=None,
                 should_consider=True):
        return Action._constraint_modifier_localized(
            job='Yielding', should_consider=should_consider, args=[
                ('in_comprehension', _in_comprehension),
                ('yield_from',_yield_from)
            ])

    def Making_Global(_id=None, should_consider=True):
        return Action._constraint_modifier_localized(
            job='Making_Global',should_consider=should_consider, args=[
                ('id', _id)
            ])

    def Making_Nonlocal(_id=None, should_consider=True):
        return Action._constraint_modifier_localized(
            job='Making_Nonlocal', should_consider=should_consider, args=[
                ('id', _id)
            ])

    def Passing(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Passing', should_consider=should_consider)

    def Returning(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Returning', should_consider=should_consider)

    def Breaking(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Breaking', should_consider=should_consider)

    def Continuing(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Continuing', should_consider=should_consider)


class Kind(object):
    _constraint_modifier_localized = partial(
        _constraint_template_modifier_func_maker, main='Kind')

    def Variables(_id=None, _is_attribute=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Variables', should_consider=should_consider, args=[
                ('id', _id), ('is_attribute', _is_attribute)
            ])

    def STD_Types(_type=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='STD_Types', should_consider=should_consider, args=[
                ('type', _type)
            ])

    def Functions(_id=None, _is_lambda=None, _is_decorator=None,
                  should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Functions', should_consider=should_consider, args=[
                ('id', _id), ('is_lambda', _is_lambda),
                ('is_decorator', _is_decorator)
            ])

    def Decorators(_id=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Decorators', should_consider=should_consider, args=[
                ('id', _id)
            ])

    def Classes(_id=None, _superclass_type=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Classes', should_consider=should_consider, args=[
                ('id', _id), ('superclass_type', _superclass_type)
            ])

    def Attributes(_id=None, _class_id=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Generators', should_consider=should_consider, args=[
                ('id', _id), ('class_id', _class_id)
            ])

    def Methods(_id=None, _class_id=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Methods', should_consider=should_consider, args=[
                ('id', _id), ('class_id', _class_id)
            ])

    def Generators(_id=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Generators', should_consider=should_consider, args=[
                ('id', _id)
            ])

    def Comprehensions(_of_list=None, _of_dict=None, _of_gen=None,
                       should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Comprehensions', should_consider=should_consider, args=[
                ('of_list', _of_list), ('of_dict', _of_dict),
                ('of_gen', _of_gen)
            ])

    def Operations(_operation_str=None, _is_unary=None, _is_binary=None,
                   should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Operations', should_consider=should_consider, args=[
                ('operation_str', _operation_str), ('is_unary', _is_unary),
                ('is_binary', _is_binary)
            ])


class Location_Limit(object):
    _constraint_modifier_localized = partial(
        _constraint_template_modifier_func_maker, main='Location_Limit')

    def Line_Numbers(starting_line=None, ending_line=None):
        return Location_Limit._constraint_modifier_localized(
            job='Line_Numbers', args=[
                ('minimum', starting_line), ('maximum', ending_line)
            ])

    def Column_Numbers(starting_column=None, ending_column=None):
        return Location_Limit._constraint_modifier_localized(
            job='Column_Numbers', args=[
                ('minimum', starting_column), ('maximum', ending_column)
            ])


class _Validators(object):
    def Action_Call(node, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Call)
        try:
            partial_validators = set([should_consider, basic_validation()])
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Initialization(node, should_consider, _knowledge):
        raise NotImplementedError

    def Action_Import(node, _id, _from, _from_id, _as, should_consider,
                      _knowledge):
        def basic_validation(node=node):
            return bool(type(node) in {ast.Import, ast.ImportFrom})

        def from_validation(is_sought, node=node):
            if is_sought:
                return bool(type(node) != ast.Import)
            else:
                return bool(type(node) != ast.ImportFrom)

        def id_validation(_id, node=node):
            return bool(_id in {sub.name for sub in node.names})

        def from_id_validation(_from_id, node=node):
            return bool(_from_id == node.module)

        def as_validation(_as, node=node):
            return bool(_as in [sub.asname for sub in node.names])

        try:
            partial_validators = set([should_consider, basic_validation()])
            if _from is not None:
                partial_validators.add(from_validation(bool(_from)))
            if _id is not None:
                partial_validators.add(id_validation(_id))
            if _from_id is not None:
                partial_validators.add(from_id_validation(_from_id))
            if _as is not None:
                partial_validators.add(as_validation(_as))
            return all(partial_validators)

        except AttributeError:
            return False

    def Action_Definition(node, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) in {ast.FunctionDef, ast.ClassDef})
        try:
            partial_validators = set([should_consider, basic_validation()])
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Assignment(node, _with_op, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) in {ast.Assign, ast.AugAssign})

        def with_op_validation(is_sought, node=node):
            if is_sought:
                return bool(type(node) is not ast.Assign)
            else:
                return bool(type(node) is not ast.AugAssign)
        try:
            partial_validators = set([should_consider, basic_validation()])
            if _with_op is not None:
                partial_validators.add(with_op_validation(bool(_with_op)))
            return all(partial_validators)

        except AttributeError:
            return False

    def Action_Assertion(node, _with_error_msg, _error_msg_content,
                         should_consider, _knowledge):

        def basic_validation(node=node):
            return bool(type(node) is ast.Assert)

        def with_error_msg_validation(is_sought, node=node):
            if is_sought:
                return bool(node.msg is not None)
            else:
                return bool(node.msg is None)

        def error_msg_content_validation(node=node):
            return bool(_error_msg_content == node.msg)

        try:
            partial_validators = set([should_consider, basic_validation()])
            if _with_error_msg is not None:
                partial_validators.add(with_error_msg_validation(bool(
                    _with_error_msg)))
            if _error_msg_content is not None:
                partial_validators.add(error_msg_content_validation())
            return all(partial_validators)

        except AttributeError:
            return False

    def Action_Looping(node, _for, _while, _for_else, _with_break,
                       _with_non_terminating_test,
                       should_consider, _knowledge):

        def regular_looping_validation(node=node):
            return bool(type(node) in {ast.For, ast.While})

        def comprehension_looping_validation(node=node):
            return bool(
                type(node) in _knowledge['comprehension_forms']
            )

        def basic_validation(node=node):
            return bool(regular_looping_validation(node=node) or
                        comprehension_looping_validation(node=node))

        def for_validation(is_sought, node=node):
            if is_sought:
                return bool(type(node) is not ast.While)
            else:
                return bool(type(node) is ast.While)

        def while_validation(is_sought, node=node):
            if is_sought:
                return bool(type(node) is ast.While)
            else:
                return bool(type(node) is not ast.While)

        def for_else_validation(is_sought, node=node):
            if is_sought:
                if (
                        regular_looping_validation(node=node) and
                        not comprehension_looping_validation(node=node)
                ):
                    return bool(len(node.orelse) != 0)
            else:
                try:
                    return bool(len(node.orelse) == 0)
                except AttributeError:
                    return True

        def with_break_validation(is_sought, node=node):
            break_presence = False
            if regular_looping_validation(node=node):
                non_looping_body = filter(
                    lambda body_element: not regular_looping_validation(
                        node=body_element
                    ), node.body
                )
                for node in non_looping_body:
                    for sub_node in ast.walk(node):
                        if type(sub_node) is ast.Break:
                            break_presence = True
                            break
                    if break_presence:
                        break
            if is_sought:
                return bool(break_presence)
            else:
                return bool(not break_presence)

        def with_non_terminating_test_validation(is_sought, node=node):
            def constant_test():
                partial_testers = {
                    'is_boolean': bool(type(node.test) is ast.NameConstant)
                }
                if bool(type(node.test) is ast.Num):
                    partial_testers['is_non_zero'] = bool(node.test.n)
                if bool(type(node.test) is ast.Str):
                    partial_testers['is_string'] = bool(node.test.s)
                return any(partial_testers.values())

            def comparison_test():
                is_comparison = bool(type(node.test) is ast.Compare)
                try:
                    result = _comparison_evaluator(node=node.test)
                except NotImplementedError:
                    result = False
                except TypeError:
                    return False
                return bool(is_comparison and bool(result))

            # Only comparators have a `test` method. By attempting to run the
            # test for a non-comparator node, we'd be raising an
            # AttributeError.
            if "test" in node.__dict__:
                constant_infinite = constant_test()
                comparison_infinite = comparison_test()
                if is_sought:
                    return bool(constant_infinite or comparison_infinite)
                else:
                    return (not bool(constant_infinite or comparison_infinite))
            return not is_sought

        try:
            partial_validators = set([should_consider, basic_validation()])
            if _for is not None:
                partial_validators.add(for_validation(bool(_for)))
            if _while is not None:
                partial_validators.add(while_validation(bool(_while)))
            if _for_else is not None:
                partial_validators.add(for_else_validation(bool(_for_else)))
            if _with_break is not None:
                partial_validators.add(with_break_validation(bool(
                    _with_break)))
            if _with_non_terminating_test is not None:
                partial_validators.add(with_non_terminating_test_validation(
                    bool(_with_non_terminating_test)))
            return all(partial_validators)

        except AttributeError:
            return False

    def Action_Conditional(node, _with_elif, _with_else, _is_ifexp,
                           should_consider, _knowledge):
        def regular_conditional_validation(node=node):
            return bool(type(node) is ast.If)

        def expressional_conditional_validation(node=node):
            return bool(type(node) is ast.IfExp)

        def comprehension_conditional_validation(node=node):
            is_in_comprehension_form = bool(
                type(node) in _knowledge['comprehension_forms']
            )
            if is_in_comprehension_form:
                for generator in node.generators:
                    if len(generator.ifs) != 0:
                        return True
            return False

        def parent_child_both_ifs_validation(node=node):
            is_if_itself = regular_conditional_validation(node=node)
            parent_is_if = regular_conditional_validation(node=node._parent)
            return (is_if_itself and parent_is_if)

        def basic_validation(node=node):
            return (
                (regular_conditional_validation(node=node) and
                 not(parent_child_both_ifs_validation(
                     node=node))
                 ) or expressional_conditional_validation(node=node) or
                comprehension_conditional_validation(node=node)
            )

        def with_elif_validation(is_sought, node=node):
            if regular_conditional_validation(node=node):
                if type(node.orelse) is list:
                    if len(node.orelse) > 0:
                        if is_sought:
                            return (bool(regular_conditional_validation(
                                node=node.orelse[0])))
                        else:
                            return (not bool(regular_conditional_validation(
                                node=node.orelse[0])))
                    else:
                        return (not is_sought)
            if (
                    comprehension_conditional_validation(node=node) or
                    expressional_conditional_validation(node=node)
            ):
                return (not is_sought)
            return False

        def with_else_validation(is_sought, node=node):
            if regular_conditional_validation(node=node):
                current_node = node
                last_else_test_is_if = False
                while regular_conditional_validation(node=current_node):
                    if type(current_node.orelse) is list:
                        if len(current_node.orelse) == 0:
                            last_else_test_is_if = True
                            break
                        else:
                            current_node = current_node.orelse[0]
                    else:
                        current_node = current_node.orelse
                if last_else_test_is_if:
                    return (not is_sought)
                else:
                    return (is_sought)
            elif expressional_conditional_validation(node=node):
                if is_sought:
                    return bool(node.orelse is not None)
                else:
                    return bool(node.orelse is None)
            elif comprehension_conditional_validation(node=node):
                return (not is_sought)
            return False

        def ifexp_validation(is_sought, node=node):
            if is_sought:
                return expressional_conditional_validation(node=node)
            else:
                return (not expressional_conditional_validation(node=node))
        try:
            partial_validators = set([should_consider, basic_validation()])
            if _with_elif is not None:
                partial_validators.add(with_elif_validation(bool(_with_elif)))
            if _with_else is not None:
                partial_validators.add(with_else_validation(bool(_with_else)))
            if _is_ifexp is not None:
                partial_validators.add(ifexp_validation(bool(_is_ifexp)))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_With(node, _as, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.With)

        def as_validation(_as):
            return any([bool(_as == with_item.optional_vars.id)
                        for with_item in node.items])
        try:
            partial_validators = set([should_consider, basic_validation()])
            if _as is not None:
                partial_validators.add(as_validation(_as))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Deletion(node, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Delete)
        try:
            partial_validators = set([should_consider, basic_validation()])
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Indexing(node, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Subscript)
        try:
            partial_validators = set([should_consider, basic_validation()])
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Trying(node, _with_except_list, _with_except_as_list,
                      _with_finally, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Try)

        def except_list_validation(
                is_sought, except_list=_with_except_list, node=node):
            if type(except_list) in {set, list}:
                except_names = set(except_name.__name__
                                   for except_name in except_list)
            else:
                except_names = {except_list.__name__}

            present_excepts = set([])
            for handler in node.handlers:
                if type(handler.type) is ast.Call:
                    present_excepts.add(handler.type.func.id)
                elif type(handler.type) in {ast.Name, ast.NameConstant}:
                    present_excepts.add(handler.type.id)

            absent_excepts = (except_names - present_excepts)
            if is_sought:
                return bool(absent_excepts == set())
            else:
                return bool(absent_excepts != set())
            return (not is_sought)

        def except_as_list_validation(
                is_sought, as_list=_with_except_as_list, node=node):
            if type(as_list) in {set, list}:
                as_names = set(as_name.__name__ for as_name in as_list)
            else:
                as_names = {str(as_list)}

            present_as_names = set([handler.name for handler in node.handlers])
            absent_as_names = (as_names - present_as_names)
            if is_sought:
                return bool(absent_as_names == set())
            else:
                return bool(absent_as_names != set())
            return (not is_sought)

        def with_finally_validation(is_sought, node=node):
            if is_sought:
                return bool(len(node.finalbody) != 0)
            else:
                return bool(len(node.finalbody) == 0)

        try:
            partial_validators = set([should_consider, basic_validation()])
            if _with_except_list is not None:
                partial_validators.add(
                    except_list_validation(is_sought=bool(_with_except_list)))
            if _with_except_as_list is not None:
                partial_validators.add(
                    except_as_list_validation(
                        is_sought=bool(_with_except_as_list)))
            if _with_finally is not None:
                partial_validators.add(
                    with_finally_validation(is_sought=bool(_with_finally)))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Raising(node, _error_type, _error_message, _cause,
                       should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Raise)

        def error_type_validation(error_type=_error_type, node=node):
            if type(node.exc) is ast.Call:
                return bool(error_type.__name__ == node.exc.func.id)
            elif type(node.exc) is ast.Name:
                return bool(error_type.__name__ == node.exc.id)
            return False

        def error_message_validation(error_message=_error_message, node=node):
            if type(node.exc) is ast.Call:
                if bool(len(node.exc.args) == 0):
                    return bool(error_message in {None, ""})
                if type(node.exc.args[0]) is ast.Str:
                    return bool(error_message == node.exc.args[0].s)
                if type(node.exc.args[0]) is ast.Num:
                    return bool(error_message == node.exc.args[0].n)
            return False

        def cause_validation(cause=_cause, node=node):
            if type(node.cause) is ast.Name:
                return bool(cause == node.cause.id)
            return False
        try:
            partial_validators = set([should_consider, basic_validation()])
            if _error_type is not None:
                partial_validators.add(error_type_validation())
            if _error_message is not None:
                partial_validators.add(error_message_validation())
            if _cause is not None:
                partial_validators.add(cause_validation())
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Yielding(node, _in_comprehension, _yield_from,
                        should_consider, _knowledge):
        def regular_yielding_validation(node=node):
            return bool(type(node) is ast.Yield)

        def in_comprehension_validation(is_sought, node=node):
            if is_sought:
                return bool(type(node) is ast.GeneratorExp)
            return bool(type(node) is not ast.GeneratorExp)

        def yield_from_validation(is_sought, node=node):
            if is_sought:
                return bool(type(node) is ast.YieldFrom)
            return bool(type(node) is not ast.YieldFrom)

        def basic_validation(node=node):
            return bool(
                regular_yielding_validation(node=node) or
                in_comprehension_validation(is_sought=True, node=node) or
                yield_from_validation(is_sought=True, node=node)
            )
        try:
            partial_validators = set([should_consider, basic_validation()])
            if _in_comprehension is not None:
                partial_validators.add(
                    in_comprehension_validation(
                        is_sought=bool(_in_comprehension)))
            if _yield_from is not None:
                partial_validators.add(yield_from_validation(
                    is_sought=bool(_yield_from)))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Making_Global(node, _id, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Global)

        def id_validation(_id=_id, node=node):
            return bool(_id in {str(name) for name in node.names})
        try:
            partial_validators = set([should_consider, basic_validation()])
            if _id is not None:
                partial_validators.add(id_validation(_id=_id))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Making_Nonlocal(node, _id, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Nonlocal)

        def id_validation(_id=_id, node=node):
            return bool(_id in {str(name) for name in node.names})
        try:
            partial_validators = set([should_consider, basic_validation()])
            if _id is not None:
                partial_validators.add(id_validation(_id=_id))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Passing(node, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Pass)
        try:
            partial_validators = set([should_consider, basic_validation()])
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Returning(node, should_consider, _knowledge):
        def regular_returning_validation(node=node):
            return bool(type(node) is ast.Return)

        def in_lambda_validation(node=node):
            return False
            raise NotImplemented

        def basic_validation(node=node):
            return bool(regular_returning_validation(node=node) or
                        in_lambda_validation(node=node))
        try:
            partial_validators = set([should_consider, basic_validation()])
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Breaking(node, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Break)
        try:
            partial_validators = set([should_consider, basic_validation()])
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Continuing(node, should_consider, _knowledge):
        def basic_validation(node=node):
            return bool(type(node) is ast.Continue)
        try:
            partial_validators = set([should_consider, basic_validation()])
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_Variables(node, _id, _is_attribute, should_consider, _knowledge):
        def regular_name_validation(node=node):
            return bool(type(node) is ast.Name)

        def builtin_type_filtering(node=node):
            return bool(type(node) not in _knowledge['builtin_types'])

        def function_filtering(node=node):
            try:
                return (bool(node != node._parent.func))
            except AttributeError:
                return True

        def class_base_filtering(node=node):
            try:
                return (bool(node not in node._parent.bases))
            except AttributeError:
                return True

        def basic_validation(node=node):
            return bool(regular_name_validation(node=node) and
                        builtin_type_filtering(node=node) and
                        function_filtering(node=node))

        def id_validation(_id, node=node):
            try:
                return bool(_id == node.id)
            except AttributeError:
                return False

        def is_attribute_validation(is_sought, node=node):
            if is_sought:
                return bool(type(node._parent) is ast.Attribute)
            else:
                return bool(type(node._parent) is not ast.Attribute)
        try:
            partial_validators = set([should_consider, basic_validation()])
            if _id is not None:
                partial_validators.add(id_validation(_id=_id))
            if _is_attribute is not None:
                partial_validators.add(is_attribute_validation(
                    is_sought=bool(_is_attribute)))
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_STD_Types(node, _type, should_consider, _knowledge):
        def basic_validation(node=node):
            if bool(type(node) is ast.Name):
                return bool(
                    node.id in [
                        builtin_type.__name__
                        for builtin_type in _knowledge['builtin_types']
                    ]
                )
            return False

        def type_name_validation(_type, node=node):
            if _type:
                return bool(node.id == _type.__name__)
            return False

        try:
            partial_validators = set([should_consider, basic_validation()])
            if _type is not None:
                partial_validators.add(type_name_validation(_type))
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_Functions(node, _id, _in_global, _is_lambda, _is_decorator,
                       should_consider, _knowledge):
        # Remove class stuff
        if not should_consider:
            return False
        try:
            lambda_check = (bool(type(node) is ast.Lambda))
            # bool((type(node) is ast.Call) and bool(node.func)))
            # function_check = bool(lambda_check or
            #                       type(node) is ast.FunctionDef)
            partial_validators = set()
            partial_validators.add(
                (type(node) in {ast.FunctionDef, ast.Lambda}) or
                (type(node) is ast.Call and bool(node.func)))
            if _id is not None:
                if type(node) is ast.Call:
                    partial_validators.add(bool(_id) and (node.func.id == _id))
                else:
                    partial_validators.add(bool(_id) and (node.name == _id))
            # if _in_global is not None:
            #     if function_check:
            #         current_node = node._parent
            #         while (type(current_node) not in {
            #                 ast.ClassDef, ast.FunctionDef, ast.Lambda}):
            #             if type(current_node) is ast.Module:
            #                 partial_validators.add(bool(_in_global))
            #                 break
            #             current_node = current_node._parent
            if _is_lambda is not None:
                partial_validators.add(bool(_is_lambda) and lambda_check)
            # if _is_decorator is not None:
            #     partial_validators.add(
            #         _is_decorator and bool(len(node.decorator_list) != 0))
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_Decorators(node, _id, should_consider, _knowledge):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(len(node.decorator_list) != 0))
            if _id is not None:
                partial_validators.add(bool(node.decorator_list[0].id == _id))
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_Classes(node, _id, _in_global, _superclass_type,
                     should_consider, _knowledge):
        # if not should_consider:
        #     return False
        # try:
        #     partial_validators = set()

        #     current_node = node
        #     module_node = None
        #     while type(current_node) is not ast.Module:
        #         if type(current_node) is ast.Module:
        #             module_node = current_node
        #         else:
        #             current_node = current_node._parent

        #     all_class_names = [class_definition.name
        #                        for class_definition in ast.walk(module_node)
        #                        if type(class_definition) is ast.ClassDef]
        #     class(bool(type(node) is ast.Name) and
        #                             bool(node.id in all_class_names)) or
        #                            bool(type(node) is ast.ClassDef))
        #     partial_validators.add((bool(type(node) is ast.Name) and
        #                             bool(node.id in all_class_names)) or
        #                            bool(type(node) is ast.ClassDef))
        #     if _in_global is not None:
        #         if type(node) is ast.ClassDef:
        #             current_node = node
        #             while (type(current_node) not in {
        #                     ast.ClassDef, ast.FunctionDef, ast.Lambda}):
        #                 if type(current_node) is ast.Module:
        #                     partial_validators.add(_in_global)
        #                     break
        #                 current_node = current_node._parent
        #         elif type(node) is ast.Name
        # except AttributeError:
        #     return False
        raise NotImplementedError

    def Kind_Attributes(node, _id, _class_id, should_consider, _knowledge):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Kind_Methods(node, _id, _class_id, should_consider, _knowledge):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Kind_Generators(_id, should_consider, _knowledge):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Kind_Comprehensions(_of_list, _of_dict, _of_gen,
                            should_consider, _knowledge):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Kind_Operations(_operation_str, _is_unary, _is_binary,
                        should_consider, _knowledge):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Location_Limit_Line_Numbers(node, _minimum, _maximum, _knowledge):
        try:
            partial_validators = set()
            if _minimum is not None:
                partial_validators.add(
                    bool(
                        isinstance(_minimum, (int, float, long)) and (
                            int(_minimum) <= node.lineno)))
            if _maximum is not None:
                partial_validators.add(
                    bool(
                        isinstance(_maximum, (int, float, long)) and (
                            int(_maximum) >= node.lineno)))
            return all(partial_validators)
        except AttributeError:
            return False

    def Location_Limit_Column_Numbers(node, _minimum, _maximum, _knowledge):
        try:
            partial_validators = set()
            if _minimum is not None:
                partial_validators.add(
                    bool(
                        isinstance(_minimum, (int, float, long)) and (
                            int(_minimum) <= node.col_offset)))
            if _maximum is not None:
                partial_validators.add(
                    bool(
                        isinstance(_maximum, (int, float, long)) and (
                            int(_maximum) >= node.col_offset)))
            return all(partial_validators)
        except AttributeError:
            return False


class _Result(object):
    def __init__(self, name, line_number, column_number):
        self.name = name.replace('.', '_')
        self.line_number = line_number
        self.column_number = column_number
        
    def __eq__(self, other):
        return bool(
            (self.name == other.name) and
            (self.line_number == other.line_number) and
            (self.column_number == other.column_number)
        )

    def __lt__(self, other):
        return bool(
            (self.line_number < other.line_number) or
            (self.column_number < other.column_number)
        )

    def __hash__(self):
        return hash((self.name, self.line_number, self.column_number))

    def __repr__(self):
        return namedtuple(self.name, "Line Column")(
            self.line_number, self.column_number
        ).__repr__()

    def __str__(self):
        return namedtuple(self.name, "Line Column")(
            self.line_number, self.column_number
        ).__str__()



class Grepper(object):
    def __init__(self, source_abs_path):
        assert os.path.exists(source_abs_path), "Path doesn't exist"
        with open(source_abs_path, 'r') as f:
            try:
                self.__ast = _establish_parent_link(ast.parse(f.read()))
                self.__source = f
                self.__name = os.path.basename(source_abs_path)
                self.__constraints_template = _Constraints_template()
                self.__knowledge_template = _update_knowledge_template(
                    ast_tree_with_parent_pointers=self.__ast,
                    knowledge_template=_Knowledge_template(),
                    results_name=self.__name
                )
            except TypeError as e:
                print(e)

    def get_source(self):
        return self.__source[:]

    def get_knowledge(self):
        return self.__knowledge_template

    def get_constraints(self):
        unfiltered_constraints = {
            constraint_type: {
                job: {
                    arg: self.__constraints_template[constraint_type][job][arg]
                    for arg in self.__constraints_template[constraint_type][
                        job]
                    if (self.__constraints_template[constraint_type][job][arg]
                        is not None)
                }
                for job in self.__constraints_template[constraint_type]
            }
            for constraint_type in self.__constraints_template
        }
        constraints = {
            constraint_type: {
                job: {
                    arg: unfiltered_constraints[constraint_type][job][arg]
                    for arg in unfiltered_constraints[constraint_type][job]
                }
                for job in unfiltered_constraints[constraint_type]
                if len(unfiltered_constraints[constraint_type][job]) != 0
            }
            for constraint_type in unfiltered_constraints
        }
        return constraints

    def reset_constraints(self):
        self.__constraints_template = _Constraints_template()

    def _validator_predicate_extracter(self):
        constraints = self.get_constraints()
        validator_predicates = {
            constraint_type: {
                job: _Validators.__dict__["{}_{}".format(constraint_type, job)]
                for job in constraints[constraint_type]
            }
            for constraint_type in constraints
        }
        validator_partial_predicates = {
            partial(validator_predicates[constraint_type][job],
                    **{(lambda key: (
                        key if key == 'should_consider' else
                        "_{}".format(key)
                    ))(key): value
                       for key, value in (
                               self.__constraints_template[
                                   constraint_type][job].items()
                       )})
            for constraint_type in validator_predicates
            for job in validator_predicates[constraint_type]
        }
        return validator_partial_predicates

    def add_constraint(self, constraint):
        assert bool(constraint.__name__ == "constraint_template_modifier"), (
            "Invalid constraint"
        )
        constraint(self.__constraints_template)

    def run(self):
        validator_predicates = self._validator_predicate_extracter()
        for node in ast.walk(self.__ast):
            if all([
                    validator_predicate(
                        node=node, _knowledge=self.get_knowledge()
                    ) for validator_predicate in validator_predicates
            ]):
                yield _Result(
                    name=self.__name,
                    line_number=node.lineno,
                    column_number=node.col_offset
                )

    def get_all_results(self):
        return list(self.run())
