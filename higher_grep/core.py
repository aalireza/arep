from collections import defaultdict, namedtuple
from functools import partial
from inspect import getfullargspec as spec
import ast
import keyword
import sys

if sys.version_info > (3, 0):
    long = int


def Constraints_template():
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
                'is_argument': None,
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


def Knowledge_template():
    _knowledge = {
        'comprehension_forms': {
            ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp
        },
        'builtins': {
            'keywords': set(set(keyword.kwlist) | {'self'}),
            'kinds': {
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
    }
    _knowledge['builtins']['types'] = {
        builtin_type
        for builtin_kind_set in _knowledge['builtins']['kinds'].values()
        for builtin_type in builtin_kind_set
    }
    _knowledge['builtins']['all'] = (set(dir(__builtins__)) |
                                     _knowledge['builtins']['keywords'])
    return _knowledge


def update_knowledge_template(
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
                        Result(
                            name=results_name,
                            line=node.lineno,
                            column=node.col_offset
                        )
                    )
            except AttributeError:
                pass

    for name_kind, names_set in name_kinds.items():
        if len(names_set):
            knowledge_template[name_kind] = names_set
    return knowledge_template


def establish_parent_link(tree):
    to_be_processed = [tree]
    while to_be_processed:
        current_parent = to_be_processed.pop(0)
        for child in ast.iter_child_nodes(current_parent):
            child._parent = current_parent
        to_be_processed.extend(list(ast.iter_child_nodes(current_parent)))
    return tree


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
        assert len(args) != 0
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


def comparison_evaluator(node):

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


def constraint_template_modifier_func_maker(main, job, should_consider=None,
                                            args=None):
    def constraint_template_modifier(template):
        if should_consider is not None:
            template[main][job]['should_consider'] = should_consider
        if args is not None:
            for key, value in args:
                template[main][job][key] = value

    return constraint_template_modifier


class Result(object):
    def __init__(self, name, line, column):
        self.name = name
        self.line = line
        self.column = column

    def __eq__(self, other):
        return bool(
            (self.name == other.name) and
            (self.line == other.line) and
            (self.column == other.column)
        )

    def __lt__(self, other):
        return bool(
            (self.name == other.name) and (
                (self.line < other.line) or
                (self.column < other.column)
            )
        )

    def __hash__(self):
        return hash((self.name, self.line, self.column))

    def __repr__(self):
        return namedtuple(self.name.replace('.', '_dot_'), "Line Column")(
            self.line, self.column
        ).__repr__()

    def __str__(self):
        return namedtuple(self.name, "Line Column")(
            self.line, self.column
        ).__str__()
