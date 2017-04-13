import ast


class Variables(object):

    def regular(node):
        # Add limitation
        return bool(type(node) is ast.Name)

    def argument(node):
        return bool(type(node) is ast.arg)

    def attribute(node):
        return bool(type(node) is ast.Attribute)

    def builtin_filtering(node, knowledge):
        if Variables.argument(node=node):
            return bool(node.arg not in knowledge['builtins']['all'])
        try:
            return bool(node.id not in knowledge['builtins']['all'])
        except AttributeError:
            return True

    def function_filtering(node):
        parent_node = node._parent
        try:
            return (bool(node != parent_node.func))
        except AttributeError:
            return True

    def class_base_filtering(node):
        try:
            return (bool(node not in node._parent.bases))
        except AttributeError:
            return True

    def class_method_filtering(node, knowledge):
        try:
            return not bool(node in knowledge['Function'])
        except AttributeError:
            return True

    def basic(node, knowledge):
        return bool(
            any([Variables.regular(node=node),
                 Variables.argument(node=node),
                 Variables.attribute(node=node)]) and
            Variables.builtin_filtering(node=node, knowledge=knowledge) and
            Variables.function_filtering(node=node) and
            Variables.class_base_filtering(node=node) and
            Variables.class_method_filtering(node=node, knowledge=knowledge)
            )

    def _id_(_id, node):
        if Variables.argument(node=node):
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
