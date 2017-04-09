import ast


class Variables(object):

    def regular(node):
        return bool(type(node) is ast.Name)

    def argument(is_sought, node):
        if is_sought is None:
            return True
        elif is_sought:
            return bool(type(node) is ast.arg)
        else:
            return bool(type(node) is not ast.arg)

    def builtin_filtering(node, knowledge):
        return bool(type(node) not in knowledge['builtins']['all'])

    def function_filtering(node):
        try:
            return (bool(node != node._parent.func))
        except AttributeError:
            return False

    def class_base_filtering(node):
        try:
            return (bool(node not in node._parent.bases))
        except AttributeError:
            return False

    # def initialization_filtering(node=node):
    #     return False

    def attribute(is_sought, node):
        if is_sought is None:
            return True
        if is_sought:
            return (bool(type(node._parent) is ast.Attribute) and
                    bool(type(node._parent._parent) is not ast.Call))
        return (bool(type(node._parent) is not ast.Attribute) or
                bool(type(node._parent._parent) is ast.Call))

    def basic(node, knowledge):
        return bool(
            any([Variables.builtin_filtering(node=node),
                 Variables.attribute(is_sought=None, node=node),
                 Variables.argument(is_sought=None, node=node)]) and
            (
                # (initialization_filtering(node=node) and
                Variables.function_filtering(node=node) and
                Variables.class_base_filtering(node=node)
            )
        )

    def _id_(_id, node):
        if Variables.argument(
                is_sought=True, node=node
        ):
            return bool(_id == node.arg)
        try:
            return bool(_id == node.id)
        except AttributeError:
            return False

    def __new__(self, node, _id, _is_attribute, _is_argument,
                should_consider, _knowledge):
        try:
            partial_validators = set([
                should_consider, self.basic(node=node, knowledge=_knowledge)
            ])
            if _id is not None:
                partial_validators.add(self._id_(_id=_id, node=node))
            if _is_attribute is not None:
                partial_validators.add(
                    Variables.attribute(
                        is_sought=bool(_is_attribute), node=node
                    )
                )
            if _is_argument is not None:
                partial_validators.add(
                    Variables.argument(is_sought=bool(_is_argument), node=node)
                )
            return all(partial_validators)
        except AttributeError:
            return False


class STD_Types(object):
    def basic(node, knowledge):
        if bool(type(node) is ast.Name):
            return bool(
                node.id in [
                    builtin_type.__name__
                    for builtin_type in knowledge['builtins']['types']
                ]
            )
        return False

    def type_name(_type, node):
        if _type:
            return bool(node.id == _type.__name__)
        return False

    def __new__(self, node, _type, should_consider, _knowledge):
        try:
            partial_validators = set([
                should_consider, self.basic(node=node, knowledge=_knowledge)
            ])
            if _type is not None:
                partial_validators.add(
                    self.type_name(_type=_type, node=node)
                )
            return all(partial_validators)
        except AttributeError:
            return False


class Functions(object):
    def __new__(self, node, _id, _is_lambda, _is_decorator,
                should_consider, _knowledge):
        raise NotImplementedError


class Decorators(object):
    def __new__(self, node, _id, should_consider, _knowledge):
        raise NotImplementedError


class Classes(object):
    def __new__(self, node, _id, _superclass_type,
                should_consider, _knowledge):
        raise NotImplementedError


class Attributes(object):
    def __new__(self, node, _id, _class_id,
                should_consider, _knowledge):
        raise NotImplementedError


class Methods(object):
    def __new__(self, node, _id, _class_id,
                should_consider, _knowledge):
        raise NotImplementedError


class Generators(object):
    def __new__(self, node, _id, should_consider, _knowledge):
        raise NotImplementedError


class Comprehensions(object):
    def __new__(self, node, _of_list, _of_dict, _of_gen,
                should_consider, _knowledge):
        raise NotImplementedError


class Operations(object):
    def __new__(self, node, _operation_str, _is_unary, _is_binary,
                should_consider, _knowledge):
        raise NotImplementedError
