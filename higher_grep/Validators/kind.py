from higher_grep.Validators.forms import ValidationForm, ValidatorForm
import ast


class Variables(object):

    def _regular(node):
        # Add limitation
        return bool(type(node) is ast.Name)

    def is_argument(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.arg)
        )

    def is_attribute(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) is ast.Attribute)
        )

    def _builtin_filtering(node, knowledge):
        if Variables.argument(node=node):
            return bool(node.arg not in knowledge['builtins']['all'])
        try:
            return bool(node.id not in knowledge['builtins']['all'])
        except AttributeError:
            return True

    def _function_filtering(node):
        parent_node = node._parent
        try:
            return (bool(node != parent_node.func))
        except AttributeError:
            return True

    def _class_base_filtering(node):
        try:
            return (bool(node not in node._parent.bases))
        except AttributeError:
            return True

    def _class_method_filtering(node, knowledge):
        try:
            return not bool(node in knowledge['Function'])
        except AttributeError:
            return True

    def basic(node, consideration, knowledge):
        return bool(
            any([Variables._regular(node),
                 Variables.is_argument(node, consideration),
                 Variables.is_attribute(node, consideration)]) and
            Variables._builtin_filtering(node, knowledge) and
            Variables._function_filtering(node) and
            Variables._class_base_filtering(node) and
            Variables._class_method_filtering(node, knowledge)
            )

    def name(name, node):
        if Variables.is_argument(node, consideration=True):
            return bool(name == node.arg)
        try:
            return bool(name == node.id)
        except AttributeError:
            return False

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class STD_Types(object):
    def basic(node, consideration, knowledge):
        return ValidationForm(
            consideration,
            condition=(
                False
                if bool(type(node) is not ast.Name)
                else (bool([
                        node.id in [
                            builtin_type.__name__
                            for builtin_type in knowledge['builtins']['types']
                        ]
                ]))
            )
        )

    def type_(type_, node):
        return ValidationForm(
            type_,
            condition=bool(node.id == type_.__name__)
        )

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
