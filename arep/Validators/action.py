from arep.utils import (comparison_evaluator, ast_operation_symbols)
from arep.Validators.forms import ValidationForm, ValidatorForm
from arep.Validators.kind import Classes
import ast

"""
The validations for Grepping of all Action constraint types are in this file.

- Every constraint type is an object with the creation method below:
    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

- Every constraint type has a method called `basic` with accepts
  `consideration`. This would return True for the most general specification
  of that type.

- If any method needs a helper function, it'd be starting with an underscore.
  They should be returning a boolean and should not possibly cause an
  AttributeError.

- The `consideration` property of all methods whose name is not `basic`, are
  the method names themselves. For example `def name(name, node)` etc.

- `knowledge` argument would be the updated knowledge template.

- All of the methods whose name are not `__new__` should ideally be
  returning a ValidationForm whose first argument is `consideration` property
  and second argument is a predicate that evaluates to `True` if the given node
  satisfies that type.
  In situations that `ValidationForm` can't be used, methods should be defined
  like below:
  if considerations is None:
      return True
  if condition_1:
      return
  if condition_2:
      return
  ...
  return not consideration

- All of the points above are valid if the constraint type has a subtype.
"""


class Call(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Call),
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Instantiation(object):
    def basic(node, consideration, knowledge):
        return ValidationForm(
            consideration,
            condition=bool(Classes._regular_call(node, knowledge))
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Import(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) in {ast.Import, ast.ImportFrom})
        )

    def name(name, node):
        if Import.basic(node, True):
            return ValidationForm(
                name,
                condition=bool(name in {sub.name for sub in node.names})
            )
        return not name

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class From(object):
        def basic(node, consideration):
            return ValidationForm(
                consideration,
                condition=bool(type(node) is ast.ImportFrom)
            )

        def name(name, node):
            if Import.From.basic(node, True):
                return ValidationForm(
                    name,
                    condition=bool(node.module == name)
                )
            return not name

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

    class As(object):
        def basic(node, consideration):
            if Import.basic(node, True):
                return ValidationForm(
                    consideration,
                    condition=any({name.asname for name in node.names})
                )
            return not consideration

        def name(name, node):
            if Import.As.basic(node, True):
                return ValidationForm(
                    name,
                    condition=bool(name in [sub.asname for sub in node.names])
                )
            return not name

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)


class Definition(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) in {ast.FunctionDef, ast.ClassDef})
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Assignment(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) in {ast.Assign, ast.AugAssign})
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class Operational_Augmentation(object):
        def basic(node, consideration):
            if Assignment.basic(node, True):
                return ValidationForm(
                    consideration,
                    condition=(bool(type(node) is ast.AugAssign))
                )
            return not consideration

        def operation_symbol(operation_symbol, node):
            if operation_symbol is None:
                return True
            if Assignment.Operational_Augmentation.basic(node, True):
                return ValidationForm(
                    operation_symbol,
                    condition=bool(
                        ast_operation_symbols()[
                            type(node.op)] == operation_symbol
                    )
                )
            return not operation_symbol

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)


class Unpacking(object):

    def _single(node):
        return (type(node) is ast.Starred)

    def _double(node):
        return (type(node) is ast.Name) and (type(node._parent) is ast.keyword)

    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(Unpacking._single(node) or Unpacking._double(node))
        )

    def one_dimensional(one_dimensional, node):
        if one_dimensional is None:
            return True
        if Unpacking.basic(node, True):
            return ValidationForm(
                one_dimensional,
                condition=bool(Unpacking._single(node))
            )
        return not one_dimensional

    def two_dimensional(two_dimensional, node):
        if two_dimensional is None:
            return True
        if Unpacking.basic(node, True):
            return ValidationForm(
                two_dimensional,
                condition=bool(Unpacking._double(node))
            )
        return not two_dimensional

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Assertion(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Assert)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class Error(object):
        def basic(node, consideration):
            if Assertion.basic(node, True):
                return ValidationForm(
                    consideration,
                    condition=(bool(node.msg.s is not None))
                )
            return not consideration

        def content(content, node):
            if Assertion.Error.basic(node, True):
                return ValidationForm(
                    content,
                    condition=bool(content == node.msg.s)
                )
            return not content

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)


class Looping(object):
    def _regular(node):
        return bool(type(node) in {ast.For, ast.While})

    def _comprehension(node, knowledge):
        return bool(type(node) in knowledge['comprehension_forms'])

    def basic(node, knowledge, consideration):
        return ValidationForm(
            consideration,
            condition=bool(
                Looping._regular(node=node) or
                Looping._comprehension(node=node, knowledge=knowledge)
            )
        )

    def for_(for_, node, knowledge):
        return ValidationForm(
            for_,
            condition=(bool(type(node) is ast.For) or
                       Looping._comprehension(node, knowledge))
        )

    def while_(while_, node):
        return ValidationForm(
            while_,
            condition=bool(type(node) is ast.While)
        )

    def for_else(for_else, node, knowledge):
        if for_else is None:
            return True
        elif for_else:
            if (
                    Looping._regular(node=node) and
                    not Looping._comprehension(node=node, knowledge=knowledge)
            ):
                return bool(len(node.orelse) != 0)
        else:
            try:
                return bool(len(node.orelse) == 0)
            except AttributeError:
                return True

    def with_break(with_break, node):
        break_presence = False
        if Looping._regular(node=node):
            non_looping_body = filter(
                lambda body_element: not Looping._regular(node=body_element),
                node.body
            )
            for node in non_looping_body:
                for sub_node in ast.walk(node):
                    if type(sub_node) is ast.Break:
                        break_presence = True
                        break
                if break_presence:
                    break
        return ValidationForm(
            with_break,
            bool(break_presence)
        )

    def with_simple_non_terminating_test(
            with_simple_non_terminating_test, node):
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
                result = comparison_evaluator(node=node.test)
            except TypeError:
                return False
            return bool(is_comparison and bool(result))

        # the test for a non-comparator node, we'd be raising an
        # AttributeError.
        if hasattr(node, "test"):
            constant_infinite = constant_test()
            comparison_infinite = comparison_test()
            return ValidationForm(
                with_simple_non_terminating_test,
                condition=bool(constant_infinite or comparison_infinite)
            )
        return not with_simple_non_terminating_test

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Conditional(object):
    def _regular(node):
        return bool(type(node) is ast.If)

    def _expression(node):
        return bool(type(node) is ast.IfExp)

    def _comprehension(node, knowledge):
        is_in_comprehension_form = bool(
            type(node) in knowledge['comprehension_forms']
        )
        if is_in_comprehension_form:
            for generator in node.generators:
                if len(generator.ifs) != 0:
                    return True
        return False

    def _parent_child_both_ifs(node):
        is_if_itself = Conditional._regular(node=node)
        parent_is_if = Conditional._regular(node=node._parent)
        return (is_if_itself and parent_is_if)

    def basic(node, knowledge, consideration):
        return ValidationForm(
            consideration,
            condition=(
                (Conditional._regular(node=node) and
                    not Conditional._parent_child_both_ifs(node=node)) or
                Conditional._expression(node=node) or
                Conditional._comprehension(node=node, knowledge=knowledge)
            )
        )

    def elif_(elif_, node, knowledge):
        if elif_ is None:
            return True
        if Conditional._regular(node=node):
            if type(node.orelse) is list:
                if len(node.orelse) > 0:
                    return ValidationForm(
                        elif_,
                        condition=bool(Conditional._regular(node.orelse[0]))
                    )
        return (not elif_)

    def else_(else_, node, knowledge):
        if else_ is None:
            return True
        if Conditional._regular(node=node):
            current_node = node
            last_else_test_is_if = False
            while Conditional._regular(node=current_node):
                if type(current_node.orelse) is list:
                    if len(current_node.orelse) == 0:
                        last_else_test_is_if = True
                        break
                    else:
                        current_node = current_node.orelse[0]
                else:
                    current_node = current_node.orelse
            return bool(else_ is not last_else_test_is_if)
        elif Conditional._expression(node=node):
            if else_:
                return bool(node.orelse is not None)
            return bool(node.orelse is None)
        elif Conditional._comprehension(
                node=node, knowledge=knowledge):
            return (not else_)
        return False

    def ifexp(ifexp, node):
        return ValidationForm(
            ifexp,
            condition=Conditional._expression(node)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class With(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.With)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class As(object):
        def basic(node, consideration):
            if With.basic(node, True):
                return ValidationForm(
                    consideration,
                    condition=(any([item.optional_vars is not None
                                    for item in node.items]))
                )
            return not consideration

        def name(node, name, consideration):
            return ValidationForm(
                consideration,
                condition=any([
                    bool(name == with_item.optional_vars.id)
                    for with_item in node.items
                ])
            )

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)


class Deletion(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Delete)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Indexing(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Subscript)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Trying(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Try)
        )

    def finally_(finally_, node):
        # Can't use ValidationForm here because node.finalbody would return an
        # AttributeError since it's being evaluated before being passed to
        # `condition`
        if finally_ is None:
            return True
        if Trying.basic(node, True):
            validity = bool(len(node.finalbody) != 0)
            if finally_:
                return validity
            return not validity
        return (not finally_)

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class Except(object):
        def basic(node, consideration):
            if consideration is None:
                return True
            if Trying.basic(node, True):
                return ValidationForm(
                    consideration,
                    condition=(any([
                        type(handler.type) in {
                            ast.Call, ast.Name, ast.NameConstant
                        } for handler in node.handlers
                    ]))
                )
            return not consideration

        def type_(type_, node):
            if type_ is None:
                return True
            if Trying.Except.basic(node, True):
                present_types = set([])
                for handler in node.handlers:
                    if type(handler.type) is ast.Call:
                        present_types.add(handler.type.func.id)
                    elif type(handler.type) in {ast.Name, ast.NameConstant}:
                        present_types.add(handler.type.id)
                return ValidationForm(
                    type_,
                    condition=bool(type_.__name__ in present_types)
                )
            return not type_

        def as_(as_, type_, node):
            if as_ is None:
                return True
            if Trying.Except.basic(node, True):
                if type_ is None:
                    return ValidationForm(
                        as_,
                        condition=bool(
                            as_ in {handler.name for handler in node.handlers}
                        )
                    )
                for handler in node.handlers:
                    if type(handler.type) is ast.Call:
                        return ValidationForm(
                            as_,
                            condition=bool(
                                (as_ == handler.name) and
                                (type_.__name__ == handler.type.func.id)
                            )
                        )
                    elif type(handler.type) in {ast.Name, ast.NameConstant}:
                        return ValidationForm(
                            as_,
                            condition=bool(
                                (as_ == handler.name) and
                                (type_.__name__ == handler.type.id)
                            )
                        )
            return not as_

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)


class Raising(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Raise)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class Error(object):
        def basic(node, consideration):
            return Raising.basic(node, consideration)

        def type_(type_, node):
            if type_ is None:
                return True
            if Raising.Error.basic(node, True):
                if type(node.exc) is ast.Call:
                    return bool(type_.__name__ == node.exc.func.id)
                elif type(node.exc) is ast.Name:
                    return bool(type_.__name__ == node.exc.id)
            return not type_

        def message(message, type_, node):
            if message is None:
                return True
            if Raising.Error.basic(node, True):
                if type(node.exc) is ast.Call:
                    corresponding_type = (
                        bool(node.exc.func.id == type_.__name__)
                        if type_ is not None
                        else True
                    )
                    if bool(len(node.exc.args) == 0):
                        return (bool(message in {None, ""}) and
                                corresponding_type)
                    if type(node.exc.args[0]) is ast.Str:
                        return (bool(message == node.exc.args[0].s) and
                                corresponding_type)
                    if type(node.exc.args[0]) is ast.Num:
                        return (bool(message == node.exc.args[0].n) and
                                corresponding_type)
            return not message

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

    class Cause(object):
        def basic(node, consideration):
            if Raising.basic(node, True):
                return ValidationForm(
                    consideration,
                    condition=bool(node.cause is not None)
                )
            return not consideration

        def name(name, type_, message, node):
            if name is None:
                return True
            if Raising.Cause.basic(node, True):
                if type(node.cause) is ast.Name:
                    corresponding = set([True])
                    if message is not None:
                        corresponding.add(
                            Raising.Error.message(message, type_, node)
                        )
                    elif type_ is not None:
                        corresponding.add(Raising.Error.type_(type_, node))
                    return bool(name == node.cause.id) and all(corresponding)
            return not name

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)


class Yielding(object):
    def _regular(node):
        return bool(type(node) is ast.Yield)

    def in_expression(in_expression, node):
        return ValidationForm(
            in_expression,
            condition=bool(type(node) is ast.GeneratorExp)
        )

    def from_(from_, node):
        return ValidationForm(
            from_,
            condition=bool(type(node) is ast.YieldFrom)
        )

    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(
                Yielding._regular(node) or
                Yielding.in_expression(True, node) or
                Yielding.from_(True, node)
            )
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Making_Global(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Global)
        )

    def name(name, node):
        if Making_Global.basic(node, True):
            return ValidationForm(
                name,
                condition=bool(
                    name in {str(node_name) for node_name in node.names}
                )
            )
        return not name

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Making_Nonlocal(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Nonlocal)
        )

    def name(name, node):
        if Making_Nonlocal.basic(node, name):
            return ValidationForm(
                name,
                condition=bool(
                    name in {str(node_name) for node_name in node.names}
                )
            )
        return not name

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Passing(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Pass)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Returning(object):
    def _regular(node):
        return bool(type(node) is ast.Return)

    def _in_lambda(node):
        return False
        raise NotImplemented

    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(Returning._regular(node) or
                           Returning._in_lambda(node))
            )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Breaking(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Break)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Continuing(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Continue)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)
