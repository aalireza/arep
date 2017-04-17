from higher_grep.Validators.forms import ValidationForm, ValidatorForm
from higher_grep.Validators import action
import ast


class Variables(object):

    def _regular(node):
        return bool(type(node) is ast.Name)

    def _argument(node):
        return bool(type(node) is ast.arg)

    def _attribute(node):
        return (Variables._regular(node) and
                bool(type(node._parent) is ast.Attribute))

    def _calling_filter(node):
        if action.Call.basic(node._parent, True):
            if node._parent.func == node:
                return False
            if type(node._parent) is ast.arguments:
                return ValidationForm(
                    True,
                    condition=bool(node in node._parent.args)
                )
        return True

    def _class_base_filter(node):
        return bool(type(node._parent) is not ast.ClassDef)

    def basic(node, consideration, knowledge):
        return ValidationForm(
            consideration,
            condition=bool(
                any([Variables._regular(node),
                     Variables._attribute(node),
                     Variables._argument(node)]) and
                Variables._calling_filter(node) and
                Variables._class_base_filter(node)
            )
        )

    def is_attribute(is_attribute, node, knowledge):
        if Variables.basic(node, True, knowledge):
            if Variables._attribute(node):
                return ValidationForm(
                    is_attribute,
                    condition=bool(
                        node._parent.attr not in knowledge['Function']
                    )
                )
        return not is_attribute

    def is_argument(is_argument, node, knowledge):
        if Variables.basic(node, True, knowledge):
            if Variables._argument(node):
                return ValidationForm(
                    is_argument,
                    condition=Variables._argument(node)
                )
        return not is_argument

    def name(name, node, knowledge):
        if node is None:
            return True
        if Variables.is_argument(name, node, knowledge):
            return ValidationForm(
                name,
                condition=bool(name == node.arg)
            )
        if Variables.is_attribute(name, node, knowledge):
            return ValidationForm(
                name,
                condition=(bool(node._parent.attr == name) or
                           bool(node.id == name))
            )
        try:
            return bool(name == node.id)
        except AttributeError:
            not name

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class STD_Types(object):
    def basic(node, consideration, knowledge):
        if consideration is None:
            return True
        if bool(type(node) is ast.Name):
            return ValidationForm(
                consideration,
                condition=bool(
                    node.id in [
                        builtin_type.__name__
                        for builtin_type in knowledge['builtins']['types']
                    ]
                )
            )
        return not consideration

    def type_(type_, node, knowledge):
        if type_ is None:
            return True
        if STD_Types.basic(node, type_, knowledge):
            return ValidationForm(
                type_,
                condition=bool(node.id == type_.__name__)
            )
        return not type_

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Functions(object):

    def _regular_def(node, knowledge):
        if bool(type(node) is ast.FunctionDef):
            return bool(node.name not in knowledge['Method'])
        return False

    def _regular_call(node, knowledge):
        # Can't check for ast.Call directly. Since a called lambda occupies
        # the same spot and messes up if one tries to put additional
        # constraints like is_builtin etc.
        if bool(type(node._parent) is ast.Call):
            # Lambdas won't have id
            if hasattr(node, "id"):
                if hasattr(node._parent, "func"):
                    if node._parent.func == node:
                        return (bool(node.id not in knowledge['Method']) and
                                bool(node.id not in knowledge['Class']))
        return False

    def _regular(node, knowledge):
        return any([Functions._regular_call(node, knowledge),
                    Functions._regular_def(node, knowledge)])

    def _lambda(node, knowledge):
        return (bool(type(node) is ast.Lambda) and
                bool(node not in knowledge['Method'][ast.Lambda]))

    def _decorator(node, knowledge):
        if type(node) is ast.Name:
            return bool(node.id in knowledge['Decorator'])
        return False

    def _name_getter(node, knowledge):
        if Functions._regular_def(node, knowledge):
            return node.name
        if (
                Functions._regular_call(node, knowledge) or
                Functions._decorator(node, knowledge)
        ):
            return node.id
        return False

    def basic(node, consideration, knowledge):
        return ValidationForm(
            consideration,
            condition=any([
                Functions._regular(node, knowledge),
                Functions._lambda(node, knowledge),
                Functions._decorator(node, knowledge)
            ])
        )

    def is_builtin(is_builtin, node, knowledge):
        if (
                Functions.basic(node, True, knowledge) and
                Functions.Lambda.basic(node, False, knowledge)
        ):
            return ValidationForm(
                is_builtin,
                condition=bool(
                    Functions._name_getter(
                        node, knowledge) in knowledge['builtins']['all']
                )
            )
        return not is_builtin

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class Lambda(object):
        def basic(node, consideration, knowledge):
            return ValidationForm(
                consideration,
                condition=Functions._lambda(node, knowledge)
            )

        def immediately_called(immediately_called, node, knowledge):
            if immediately_called is None:
                return True
            if Functions.Lambda.basic(node, True, knowledge):
                return ValidationForm(
                    immediately_called,
                    condition=(
                        bool(type(node._parent) is ast.Call) and
                        bool(node.lineno == node._parent.lineno) and
                        bool(node.col_offset == node._parent.col_offset)
                    )
                )
            return not immediately_called

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

    class Decorators(object):
        def basic(node, consideration, knowledge):
            return ValidationForm(
                consideration,
                condition=Functions._decorator(node, knowledge)
            )

        def name(name, node, knowledge):
            if name is None:
                return True
            if Functions.Decorators.basic(node, True, knowledge):
                return ValidationForm(
                    name,
                    condition=bool(
                        Functions._name_getter(node, knowledge) == name
                    )
                )
            return not name

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)


class Classes(object):
    def basic(node, consideration):
        raise NotImplementedError

    def name(name, consideration):
        raise NotImplementedError

    def bases_list(bases_list, node):
        raise NotImplementedError

    def attributes_list(attributes_list, node):
        raise NotImplementedError

    def methods_list(methods_list, node):
        raise NotImplementedError

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Generators(object):
    def basic(node, consideration):
        raise NotImplementedError

    def name(name, node):
        raise NotImplementedError

    def is_expression(is_expression, node):
        raise NotImplementedError

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Comprehensions(object):
    def basic(node, consideration):
        raise NotImplementedError

    def of_list(of_list, node):
        raise NotImplementedError

    def of_set(of_set, node):
        raise NotImplementedError

    def of_dict(of_dict, node):
        raise NotImplementedError

    def of_gen(of_gen, node):
        raise NotImplementedError

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Operations(object):
    def basic(node, consideration):
        raise NotImplementedError

    def stringified_operation(stringified_operation, node):
        raise NotImplementedError

    def is_unary(is_unary, consideration):
        raise NotImplementedError

    def is_binary(is_binary, consideration):
        raise NotImplementedError
