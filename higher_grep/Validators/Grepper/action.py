from higher_grep.core import comparison_evaluator
from higher_grep.Validators import ValidationForm, ValidatorForm
import ast


class Call(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Call),
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Initialization(object):
    def basic(node):
        pass

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Import(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) in {ast.Import, ast.ImportFrom})
        )

    def name(node, name, consideration):
        return ValidationForm(
            consideration,
            condition=bool(name in {sub.name for sub in node.names})
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class From(object):
        def basic(node, consideration):
            return ValidationForm(
                consideration,
                condition=bool(type(node) is ast.ImportFrom)
            )

        def name(node, name, consideration):
            return ValidationForm(
                consideration,
                condition=bool(node.id == name)
            )

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

    class As(object):
        def basic(node, consideration):
            return ValidationForm(
                consideration,
                condition=(bool(len(node.names) != 0) and
                           Import.basic(node, True))
            )

        def name(node, name, consideration):
            return ValidationForm(
                consideration,
                condition=bool(name in [sub.asname for sub in node.names])
            )

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
            return ValidationForm(
                consideration,
                condition=bool(type(node) is ast.AugAssign)
            )

        def operation(node):
            pass

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
            return ValidationForm(
                consideration,
                condition=(bool(node.msg is not None) and
                           Assertion.basic(node, True))
            )

        def content(node, content, consideration):
            return ValidationForm(
                consideration,
                condition=bool(content == node.msg)
            )

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

    def for_(for_, node):
        return ValidationForm(
            for_,
            condition=bool(type(node) is ast.For)
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
            bool(with_break == break_presence)
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
            except NotImplementedError:
                result = False
            except TypeError:
                return False
            return bool(is_comparison and bool(result))

        # Only comparators have a `test` method. By attempting to run
        # the test for a non-comparator node, we'd be raising an
        # AttributeError.
        # if "test" in node.__dict__:
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

    def parent_child_both_ifs(node):
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
                else:
                    return (not elif_)
        if (
                Conditional.comprehension(node=node, knowledge=knowledge) or
                Conditional.expression(node=node)
        ):
            return (not elif_)
        return False

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
        elif Conditional.expression(node=node):
            if else_:
                return bool(node.orelse is not None)
            return bool(node.orelse is None)
        elif Conditional.comprehension(
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
            return ValidationForm(
                consideration,
                condition=(bool(len(node.items) != 0) and
                           With.basic(node, True))
            )

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
        return ValidationForm(
            finally_,
            condition=bool(len(node.finalbody != 0))
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class Except(object):
        def basic(node, consideration):
            return ValidationForm(
                consideration,
                condition=(
                    any([type(handler.type) in {ast.Call,
                                                ast.Name,
                                                ast.NameConstant}
                         for handler in node.handlers]) and
                    Trying.basic(node, True)
                )
            )

        def type_(type_, node):
            present_types = set([])
            for handler in node.handlers:
                if type(handler.type) is ast.Call:
                    present_types.add(handler.type.func.id)
                elif type(handler.type) in {ast.Name, ast.NameConstant}:
                    present_types.add(handler.type.id)
            return ValidationForm(
                type_,
                condition=bool(type_ in present_types)
            )

        def as_(as_, node):
            return ValidationForm(
                as_,
                condition=bool(
                    as_ in {handler.name for handler in node.handlers}
                )
            )

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)


class Raising(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Raise)
        )

    def __new__(self, **kwargs):
        return ValidationForm(self, **kwargs)

    class Error(object):
        def basic(node, consideration):
            return Raising.basic(node, consideration)

        def type_(type_, node):
            if type_ is None:
                return True
            if type(node.exc) is ast.Call:
                return bool(type_.__name__ == node.exc.func.id)
            elif type(node.exc) is ast.Name:
                return bool(type_.__name__ == node.exc.id)
            return False

        def message(message, node):
            if message is None:
                return True
            if type(node.exc) is ast.Call:
                if bool(len(node.exc.args) == 0):
                    return bool(message in {None, ""})
                if type(node.exc.args[0]) is ast.Str:
                    return bool(message == node.exc.args[0].s)
                if type(node.exc.args[0]) is ast.Num:
                    return bool(message == node.exc.args[0].n)
            return False

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

    class Cause(object):
        def basic(node, consideration):
            return ValidationForm(
                consideration,
                condition=(bool(node.case is not None) and
                           Raising.basic(node, True))
                )

        def name(name, node):
            if name is None:
                return True
            if type(node.cause) is ast.Name:
                return bool(name == node.cause.id)
            return False

        def __new__(self, **kwargs):
            return ValidationForm(self, **kwargs)


class Yielding(object):
    def _regular(node):
        return bool(type(node) is ast.Yield)

    def in_expression(node):
        return bool(type(node) is ast.GeneratorExp)

    def from_(from_, node):
        return ValidationForm(
            from_,
            condition=bool(type(node) is ast.YieldFrom)
        )

    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(
                Yielding._regular(node=node) or
                Yielding.in_expression(node=node) or
                Yielding.from_(consideration, node)
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
        return ValidationForm(
            name,
            condition=bool(
                name in {str(node_name) for node_name in node.names}
            )
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Making_Nonlocal(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Nonlocal)
        )

    def name(name, node):
        return ValidationForm(
            name,
            condition=bool(
                name in {str(node_name) for node_name in node.names}
            )
        )

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
            condition=bool(type(node) is ast.Continuing)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)
