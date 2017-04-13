from collections import defaultdict, namedtuple
from functools import partial
from inspect import getfullargspec as spec
import ast
import keyword
import sys

if sys.version_info > (3, 0):
    long = int

class Validators(object):
    class Call(object):
        def basic(node):
            return bool(type(node) is ast.Call)

        def __new__(self, node, consideration, knowledge):
            try:
                validators = set([consideration, self.basic(node=node)])
                return all(validators)
            except AttributeError:
                return False



class TemplateMaker(type):

    def __new__(cls, name, parents, specs):

        non_representables = {
            *{
                '__repr__', '__delattr__', '__setattr__', '__dict__',
                '__name__', '__iter__', '__str__', '__getitem__',
            },
            '__itername__', 'view_actives', 'reset', '_class_vars', '_methods',
        }

        def set_attr_decorated(cls, name, value):
            if name == name.capitalize():
                raise TypeError("Can't set a value for a constraint type")

            if not hasattr(cls, name):
                raise KeyError(
                    "Can't set an attribute that wasn't in the template"
                )

            if name != "consideration":
                object.__setattr__(cls, "consideration", True)

            object.__setattr__(cls, name, value)

        def del_attr_decorated(cls, name):
            raise Exception("Can't delete any part of the template")

        def get_item_decorated(cls, key):
            if key not in non_representables:
                return getattr(cls, key)
            raise KeyError(
                "{} doesn't have the requested specification".format(
                    cls.__name__
                )
            )

        def view_actives(cls):
            results = dict()
            for key_name, key in zip(cls.__itername__(), cls):
                if key_name in cls._class_vars:
                    if key is not None:
                        results[key_name] = key
                elif key_name in cls._methods:
                    key_if_active = view_actives(key)
                    if key_if_active:
                        results[key_name] = key_if_active
            return results

        def reset(cls, replace_with=None):
            for attr in cls.__itername__():
                if attr not in non_representables:
                    if type(getattr(cls, attr)).__name__ == "Constraint":
                        reset(getattr(cls, attr), replace_with)
                    else:
                        setattr(cls, attr, replace_with)

        def wrapped(name, specs, with_consideration):
            if type(specs) is not dict:
                return specs

            if any([type(specs[key]) is dict for key in specs]):
                for key in specs:
                    try:
                        specs[key] = wrapped(
                            key, specs[key], with_consideration
                        )
                    except AttributeError:
                        print(key)

            specs['__name__'] = name

            if with_consideration:
                specs['consideration'] = None

            specs['__setattr__'] = set_attr_decorated

            specs['__delattr__'] = del_attr_decorated

            specs['__getitem__'] = get_item_decorated

            specs['__iter__'] = (
                lambda cls: (
                    getattr(cls, key)
                    for key in cls.__itername__()
                    if key not in non_representables
                )
            )

            specs['__itername__'] = (
                lambda cls: (
                    key
                    for key in specs
                    if key not in non_representables
                )
            )

            specs['__repr__'] = (
                lambda cls: (
                    {
                        str(key): getattr(cls, str(key))
                        for key in cls.__itername__()
                        if key not in non_representables
                    }.__repr__()
                ).replace("'", "")
            )

            specs['__str__'] = (lambda cls: cls.__name__)

            specs['reset'] = (
                lambda cls, resetting_value=None: reset(cls, resetting_value)
            )

            specs['view_actives'] = (
                lambda cls: view_actives(cls)
            )

            specs['_class_vars'] = {
                key: value
                for key, value in specs.items()
                if (key == key.lower()) and (key not in non_representables)
            }

            specs['_methods'] = {
                key: value
                for key, value in specs.items()
                if ((key not in specs['_class_vars']) and
                    (key not in non_representables))
            }

            return type("Constraint", (object,), specs)()

        specs['__name__'] = name
        with_consideration = specs['considerable']
        del specs['considerable']

        return wrapped(name, specs, with_consideration)


class Action(object):
    __Template_Form = {
        'considerable': True,
        'Call': dict(),
        'Initialization': dict(),
        'Import': {
            'name': None,
            'From': {
                'name': None,
            },
            'As': {
                'name': None,
            }
        },
        'Definition': dict(),
        'Assignment': {
            'Operational_Augmentation': {
                'operation': None
            }
        },
        'Assertion': {
            'Error': {
                'content': None
            }
        },
        'Looping': {spec: None for spec in {
            'for_', 'while_', 'for_else', 'with_break',
            'with_simple_non_terminating_test'
        }},
        'Conditional': {spec: None for spec in {
            'elif_', 'else_', 'ifexp'
        }},
        'With': {
            'As': {
                'name': None
            }
        },
        'Deletion': dict(),
        'Indexing': dict(),
        'Trying': {
            'Except': {
                'type': None,
                'as_': None
            },
            'Finally': dict(),
        },
        'Raising': {
            'Error': {
                'type': None,
                'message': None
            },
            'Cause': {
                'name': None
            },
        },
        'Yielding': {
            'From': dict(),
            'In_GeneratorExp': dict(),
        },
        **{
            specs: {'name': None}
            for specs in {
                    'Making_Global', 'Making_Nonlocal', 'Passing',
                    'Returning', 'Breaking', 'Continuing'}
        },

    }

    def __new__(self):
        return TemplateMaker("Action", (object,), self.__Template_Form.copy())


class Kind(object):
    __Template_Form = {
        'considerable': True,
        'Variables': {
            spec: None
            for spec in {
                    'name', 'is_attribute', 'is_argument'
            }
        },
        'STD_Types': {
            'type': None
        },
        'Functions': {
            spec: None
            for spec in {
                    'name', 'is_lambda', 'is_decorator'
            }
        },
        'Classes': {
            'name': None,
            'Bases': {
                'list_': None,
            }
        },
        'Attributes': {
            'name': None,
            'Of_Class': {
                'name': None
            }
        },
        'Methods': {
            'name': None,
            'Of_Class': {
                'name': None
            }
        },
        'Generators': {
            'name': None,
            'is_expression': None,
        },
        'Comprehensions': {
            spec: None for spec in {
                'of_list', 'of_set', 'of_dict', 'of_gen'
            }
        },
        'Operations': {
            'stringified_value': None,
            'is_unary': None,
            'is_binary': None,
        }
    }

    def __new__(self):
        return TemplateMaker("Kind", (object,), self.__Template_Form.copy())


class Limit(object):
    __Template_Form = {
        'considerable': False,
        'Positional': {
            **{
                key: {
                    'minimum': None,
                    'maximum': None
                } for key in {'Line_Numbers', 'Column_Numbers'}
            }
        }
    }

    def __new__(self):
        return TemplateMaker("Limit", (object,), self.__Template_Form.copy())


class Constraint(object):
    def __init__(self):
        self.__template = namedtuple(
            "Constraints", "Action Kind Limit"
        )(Action(), Kind(), Limit())

        self.Action = self.__template.Action
        self.Kind = self.__template.Kind
        self.Limit = self.__template.Limit

    def reset(self, replace_with=None):
        self.Action.reset(replace_with)
        self.Kind.reset(replace_with)
        self.Limit.reset(replace_with)

    def view_actives(self):
        return {
            key: value.view_actives()
            for key, value in {
                    ('Action', self.Action),
                    ('Kind', self.Kind),
                    ('Limit', self.Limit)
            } if bool(value.view_actives())
        }

    def __iter__(self):
        for constraint in [self.Action, self.Kind, self.Limit]:
            yield constraint

    def __repr__(self):
        return {
            constraint.__name__: constraint
            for constraint in {self.Action, self.Kind, self.Limit}
        }.__repr__().replace("'", "")

    def __str__(self):
        return "Constraint"
        # return "{}=({})".format("Constraints", ", ".join([
        #     x.__name__ for x in {self.Action, self.Kind, self.Limit}
        # ]))


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
    knowledge['builtins']['all'] = (set(dir(__builtins__)) |
                                    knowledge['builtins']['keywords'])
    return knowledge


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
            (ast.Gte, ast.Lt),
            (ast.Gt, ast.LtE),
    }:
        ast_mappings[ast_not_operation] = ast_mappings[ast.Not](
            ast_mappings[previously_defined_ast_operation]
        )
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
