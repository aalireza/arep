from collections import defaultdict, namedtuple
from functools import partial
from inspect import getfullargspec as spec
import ast
import builtins
import keyword
import sys

if sys.version_info > (3, 0):
    long = int


def Knowledge_template():
    knowledge = {
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
    knowledge['builtins']['types'] = {
        builtin_type
        for builtin_kind_set in knowledge['builtins']['kinds'].values()
        for builtin_type in builtin_kind_set
    }
    knowledge['builtins']['all'] = (set(dir(builtins)) |
                                    knowledge['builtins']['keywords'])
    return knowledge


def update_knowledge_template(
        ast_tree_with_parent_pointers, knowledge_template, results_name,
        _with_classes=True, _with_funcs=True, _with_decorators=True,
        _with_class_methods=True):

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

    def decorator_name_checker(node):
        if type(node) is ast.Name:
            if hasattr(node._parent, "decorator_list"):
                if node in node._parent.decorator_list:
                    return ('Decorator', node.id)

    def class_method_name_checker(node):

        def contained_in_class(node):
            if hasattr(node, "_parent"):
                if type(node._parent) is ast.ClassDef:
                    return True
                if type(node._parent) in {ast.FunctionDef, ast.Lambda}:
                    return False
                return contained_in_class(node._parent)
            return False

        if type(node) in {ast.Lambda, ast.FunctionDef}:
            if contained_in_class(node):
                return ('Method', (ast.Lambda
                                   if type(node) is ast.Lambda
                                   else node.name))
        return False

    name_kinds = {
        key: defaultdict(list)
        for key in {'Function', 'Class', 'Decorator', 'Method'}
    }
    name_checkers = set([])
    if _with_funcs:
        name_checkers.add(func_name_checker)
    if _with_classes:
        name_checkers.add(class_name_checker)
    if _with_decorators:
        name_checkers.add(decorator_name_checker)
    if _with_class_methods:
        name_checkers.add(class_method_name_checker)
    for node in ast.walk(ast_tree_with_parent_pointers):
        for name_checker in name_checkers:
            try:
                result = name_checker(node)
                if result:
                    name_kinds[result[0]][result[1]].append(node)
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


def count_arity_ast(node):
    if type(node) in {ast.Lambda, ast.FunctionDef}:
        if any(
                [getattr(node.arguments, cat) is not None
                 for cat in {"vararg", "kwarg"}]
        ):
            return float("inf")
        return len(node.arguments.args)
    return None


def _ast_mapped_operators():

    def basic_reducer(definition, *args):
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

    ast_mappings = {
        ast_operation: partial(basic_reducer, definition)
        for ast_operation, definition in {
            (ast.Is, lambda x, y:  y if x is y else None),
            (ast.Not, lambda x: not x),
            (ast.And, lambda x, y: x and y),
            (ast.Or, lambda x, y: x or y),
            (ast.In, lambda x, y: x in y),
            (ast.Eq, lambda x, y: x == y),
            (ast.Lt, lambda x, y: x < y),
            (ast.UAdd, lambda x: +x),
            (ast.USub, lambda x: -x),
            (ast.Add, lambda x, y: x + y),
            (ast.Sub, lambda x, y: x - y),
            (ast.Mult, lambda x, y: x * y),
            (ast.Div, lambda x, y: x / y),
            (ast.FloorDiv, lambda x, y: x // y),
            (ast.Mod, lambda x, y: x % y),
            (ast.Pow, lambda x, y: x ** y),
            (ast.MatMult, lambda x, y: x @ y),
            (ast.Invert, lambda x: ~x),
            (ast.LShift, lambda x, y: x << y),
            (ast.RShift, lambda x, y: x >> y),
            (ast.BitAnd, lambda x, y: x & y),
            (ast.BitOr, lambda x, y: x | y),
            (ast.BitXor, lambda x, y: x ^ y)
        }
    }
    ast_mappings[ast.LtE] = (
        lambda x, y: (ast_mappings[ast.Lt](x, y) or
                      ast_mappings[ast.Eq](x, y))
    )
    for ast_not_operation, previously_defined_ast_operation in {
            (ast.IsNot, ast.Is),
            (ast.NotIn, ast.In),
            (ast.NotEq, ast.Eq),
            (ast.GtE, ast.Lt),
            (ast.Gt, ast.LtE),
    }:
        ast_mappings[ast_not_operation] = (
            lambda *args: ast_mappings[ast.Not](
                ast_mappings[previously_defined_ast_operation](*args)
            )
        )
    return ast_mappings


def comparison_evaluator(node):

    def type_seive(comparator):
        if bool(type(comparator) is ast.Num):
            return comparator.n
        elif bool(type(comparator) is ast.Str):
            return comparator.s
        return comparator

    if not bool(type(node) is ast.Compare):
        raise TypeError("{} is not a comparator".format(node))
    operations = _ast_mapped_operators()
    left = type_seive(node.left)
    for op, comparator in zip(
            map(lambda op: operations[type(op)], node.ops),
            node.comparators
    ):
        print(node, op, comparator)
        left = op(left, type_seive(comparator))

    return left


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
                ((self.line == other.line) and
                 (self.column < other.column))
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
