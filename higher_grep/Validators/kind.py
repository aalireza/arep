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
    def basic(node, consideration):
        raise NotImplementedError

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class Lambda(object):
        def basic(node, consideration):
            raise NotImplementedError

        def immediately_called(node, consideration):
            raise NotImplementedError

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

    class Decorator(object):
        def basic(node, consideration):
            raise NotImplementedError

        def name(name, node):
            raise NotImplementedError

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
