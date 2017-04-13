from higher_grep.core import comparison_evaluator
from inspect import getfullargspec as spec
import ast


def ValidatorForm(**kwargs):
    def func_call_from_kwargs(f, keyword_dict):
        return f(**{
            key: keyword_dict[key]
            for key in keyword_dict
            if key in spec(f).args
        })

    cls = kwargs['cls']
    try:
        validators = set([
            kwargs['consideration'], func_call_from_kwargs(cls.basic, kwargs)
        ])
        for kwarg in kwargs:
            if kwarg not in {
                    *list(spec(cls.basic).args),
                    'consideration', 'knowledge'
            }:
                validators.add(func_call_from_kwargs(
                    getattr(cls, kwarg), kwargs
                ))
        return all(validators)
    except AttributeError:
        return False


class Call(object):
    def basic(node):
        return bool(type(node) is ast.Call)

    def __new__(self, node, consideration, knowledge):
        try:
            validators = set([consideration, self.basic(node=node)])
            return all(validators)
        except AttributeError:
            return False


class Initialization(object):
    def basic(node):
        pass

    def __new__(self, node, consideration, knowledge):
        pass


class Import(object):

    class From(object):
        def basic(self, node):
            return bool(type(node) is ast.ImportFrom)

        def name(self, name, node):
            return bool(node.id == name)

        def __new__(self, node, name, consideration, knowledge):
            try:
                validators = set([consideration, self.basic(node)])
                if name is not None:
                    validators.add(self.name(node, name))
                return all(validators)
            except AttributeError:
                return False

    class As(object):
        def basic(self, node, name):
            return bool(name in [sub.asname for sub in node.names])

        def __new__(self, node, name, consideration, knowledge):
            try:
                validators = set([consideration, self.basic(node, name)])
                return all(validators)
            except AttributeError:
                return False

    def basic(node):
        return bool(type(node) in {ast.Import, ast.ImportFrom})

    def name(name, node):
        return bool(name in {sub.name for sub in node.names})

    def __new__(self, node, name, consideration, knowledge):
        try:
            partial_validators = set([consideration, self.basic(node)])
            if name is not None:
                partial_validators.add(self.name(name, node))
            return all(partial_validators)
        except AttributeError:
            return False


class Definition(object):
    def basic(node):
        return bool(type(node) in {ast.FunctionDef, ast.ClassDef})

    def __new__(self, node, consideration, knowledge):
        try:
            validators = set([consideration, self.basic(node)])
            return all(validators)
        except AttributeError:
            return False


class Assignment(object):
    class Operational_Augmentation(object):
        def basic(node):
            return bool(type(node) is ast.AugAssign)

        def __new__(self, node, operation, consideration, knowledge):
            try:
                validators = set([consideration, self.basic(node)])
                if operation is not None:
                    validators.add(self.operation(operation, node, knowledge))
                return all(validators)
            except AttributeError:
                return False

    def basic(node):
        return bool(type(node) in {ast.Assign, ast.AugAssign})

    def __new__(self, node, consideration, knowledge):
        try:
            validators = set([consideration, self.basic(node)])
            return all(validators)
        except AttributeError:
            return False


class Assertion(object):
    def basic(node):
        return bool(type(node) is ast.Assert)

    def with_error_msg(is_sought, node):
        if is_sought:
            return bool(node.msg is not None)
        return bool(node.msg is None)

    def error_msg_content(_error_msg_content, node):
        return bool(_error_msg_content == node.msg)

    def __new__(self, node, _with_error_msg, _error_msg_content,
                consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            if _with_error_msg is not None:
                partial_validators.add(
                    self.with_error_msg(
                        is_sought=bool(_with_error_msg), node=node
                    )
                )
            if _error_msg_content is not None:
                partial_validators.add(
                    self.error_msg_content(
                        _error_msg_content=_error_msg_content,
                        node=node
                    )
                )
            return all(partial_validators)
        except AttributeError:
            return False


class Looping(object):

    def regular(node):
        return bool(type(node) in {ast.For, ast.While})

    def comprehension(node, knowledge):
        return bool(type(node) in knowledge['comprehension_forms'])

    def basic(node, knowledge):
        return bool(
            Looping.regular(node=node) or
            Looping.comprehension(node=node, knowledge=knowledge)
        )

    def _for_(is_sought, node):
        if is_sought:
            return bool(type(node) is not ast.While)
        return bool(type(node) is ast.While)

    def _while_(is_sought, node):
        if is_sought:
            return bool(type(node) is ast.While)
        return bool(type(node) is not ast.While)

    def for_else(is_sought, node, knowledge):
        if is_sought:
            if (
                    Looping.regular(node=node) and
                    not Looping.comprehension(node=node, knowledge=knowledge)
            ):
                return bool(len(node.orelse) != 0)
        else:
            try:
                return bool(len(node.orelse) == 0)
            except AttributeError:
                return True

    def with_break(is_sought, node):
        break_presence = False
        if Looping.regular(node=node):
            non_looping_body = filter(
                lambda body_element: not Looping.regular(node=body_element),
                node.body
            )
            for node in non_looping_body:
                for sub_node in ast.walk(node):
                    if type(sub_node) is ast.Break:
                        break_presence = True
                        break
                if break_presence:
                    break
        return bool(is_sought == break_presence)

    def with_non_terminating_test(is_sought, node):
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
            if is_sought:
                return bool(constant_infinite or comparison_infinite)
            return (not bool(constant_infinite or comparison_infinite))
        return not is_sought

    def __new__(self, node, _for, _while, _for_else, _with_break,
                _with_non_terminating_test,
                consideration, _knowledge):
        try:
            partial_validators = set([
                consideration, self.basic(node=node, knowledge=_knowledge)
            ])
            if _for is not None:
                partial_validators.add(
                    self._for_(is_sought=bool(_for), node=node)
                )
            if _while is not None:
                partial_validators.add(
                    self._while_(is_sought=bool(_while), node=node)
                )
            if _for_else is not None:
                partial_validators.add(
                    self.for_else(
                        is_sought=bool(_for_else), node=node,
                        knowledge=_knowledge
                    )
                )
            if _with_break is not None:
                partial_validators.add(
                    self.with_break(
                        is_sought=bool(_with_break), node=node
                    )
                )
            if _with_non_terminating_test is not None:
                partial_validators.add(
                    self.with_non_terminating_test(
                        is_sought=bool(_with_non_terminating_test), node=node
                    )
                )
            return all(partial_validators)
        except AttributeError:
            return False


class Conditional(object):
    def regular(node):
        return bool(type(node) is ast.If)

    def expression(node):
        return bool(type(node) is ast.IfExp)

    def comprehension(node, knowledge):
        is_in_comprehension_form = bool(
            type(node) in knowledge['comprehension_forms']
        )
        if is_in_comprehension_form:
            for generator in node.generators:
                if len(generator.ifs) != 0:
                    return True
        return False

    def parent_child_both_ifs(node):
        is_if_itself = Conditional.regular(
            node=node)
        parent_is_if = Conditional.regular(
            node=node._parent)
        return (is_if_itself and parent_is_if)

    def basic(node, knowledge):
        return (
            (Conditional.regular(node=node) and
                not Conditional.parent_child_both_ifs(node=node)) or
            Conditional.expression(node=node) or
            Conditional.comprehension(node=node, knowledge=knowledge)
        )

    def with_elif(is_sought, node, knowledge):
        if Conditional.regular(node=node):
            if type(node.orelse) is list:
                if len(node.orelse) > 0:
                    if is_sought:
                        return (bool(Conditional.regular(node=node.orelse[0])))
                    else:
                        return (not bool(
                            Conditional.regular(node=node.orelse[0])
                        ))
                else:
                    return (not is_sought)
        if (
                Conditional.comprehension(node=node, knowledge=knowledge) or
                Conditional.expression(node=node)
        ):
            return (not is_sought)
        return False

    def with_else(is_sought, node, knowledge):
        if Conditional.regular(node=node):
            current_node = node
            last_else_test_is_if = False
            while Conditional.regular(node=current_node):
                if type(current_node.orelse) is list:
                    if len(current_node.orelse) == 0:
                        last_else_test_is_if = True
                        break
                    else:
                        current_node = current_node.orelse[0]
                else:
                    current_node = current_node.orelse
            return bool(is_sought is not last_else_test_is_if)
        elif Conditional.expression(node=node):
            if is_sought:
                return bool(node.orelse is not None)
            return bool(node.orelse is None)
        elif Conditional.comprehension(
                node=node, knowledge=knowledge):
            return (not is_sought)
        return False

    def ifexp(is_sought, node):
        return bool(is_sought is Conditional.expression(node=node))

    def __new__(self, node, _with_elif, _with_else, _is_ifexp,
                consideration, _knowledge):
        try:
            partial_validators = set([
                consideration, self.basic(node=node, knowledge=_knowledge)
            ])
            if _with_elif is not None:
                partial_validators.add(
                    self.with_elif(is_sought=bool(_with_elif),
                                   node=node, knowledge=_knowledge)
                )
            if _with_else is not None:
                partial_validators.add(
                    self.with_else(is_sought=bool(_with_else),
                                   node=node, knowledge=_knowledge)
                )
            if _is_ifexp is not None:
                partial_validators.add(
                    self.ifexp(is_sought=bool(_is_ifexp), node=node)
                )
            return all(partial_validators)
        except AttributeError:
            return False


class With(object):
    def basic(node):
        return bool(type(node) is ast.With)

    def _as_(_as, node):
        return any([bool(_as == with_item.optional_vars.id)
                    for with_item in node.items])

    def __new__(self, node, _as, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            if _as is not None:
                partial_validators.add(self._as_(_as=_as, node=node))
            return all(partial_validators)
        except AttributeError:
            return False


class Deletion(object):
    def basic(node):
        return bool(type(node) is ast.Delete)

    def __new__(self, node, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            return all(partial_validators)
        except AttributeError:
            return False


class Indexing(object):
    def basic(node):
        return bool(type(node) is ast.Subscript)

    def __new__(self, node, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            return all(partial_validators)
        except AttributeError:
            return False


class Trying(object):
    def basic(node):
        return bool(type(node) is ast.Try)

    def except_list(is_sought, except_list, node):
        if type(except_list) in {set, list}:
            except_names = set(
                except_name.__name__
                for except_name in except_list
            )
        else:
            except_names = {except_list.__name__}

        present_excepts = set([])
        for handler in node.handlers:
            if type(handler.type) is ast.Call:
                present_excepts.add(handler.type.func.id)
            elif type(handler.type) in {ast.Name, ast.NameConstant}:
                present_excepts.add(handler.type.id)

        absent_excepts = (except_names - present_excepts)
        if is_sought:
            return bool(absent_excepts == set())
        else:
            return bool(absent_excepts != set())
        return (not is_sought)

    def except_as_list(is_sought, as_list, node):
        if type(as_list) in {set, list}:
            as_names = set(as_name.__name__ for as_name in as_list)
        else:
            as_names = {str(as_list)}

        present_as_names = set(
            handler.name for handler in node.handlers
        )
        absent_as_names = (as_names - present_as_names)
        if is_sought:
            return bool(absent_as_names == set())
        else:
            return bool(absent_as_names != set())
        return (not is_sought)

    def with_finally(is_sought, node):
        if is_sought:
            return bool(len(node.finalbody) != 0)
        return bool(len(node.finalbody) == 0)

    def __new__(self, node, _with_except_list, _with_except_as_list,
                _with_finally, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            if _with_except_list is not None:
                partial_validators.add(
                    self.except_list(
                        is_sought=bool(_with_except_list),
                        except_list=_with_except_list,
                        node=node
                    )
                )
            if _with_except_as_list is not None:
                partial_validators.add(
                    self.except_as_list(
                        is_sought=bool(_with_except_as_list),
                        as_list=_with_except_as_list,
                        node=node
                    )
                )
            if _with_finally is not None:
                partial_validators.add(
                    self.with_finally(is_sought=bool(_with_finally), node=node)
                )
            return all(partial_validators)
        except AttributeError:
            return False


class Raising(object):
    def basic(node):
        return bool(type(node) is ast.Raise)

    def error_type(error_type, node):
        if type(node.exc) is ast.Call:
            return bool(error_type.__name__ == node.exc.func.id)
        elif type(node.exc) is ast.Name:
            return bool(error_type.__name__ == node.exc.id)
        return False

    def error_message(error_message, node):
        if type(node.exc) is ast.Call:
            if bool(len(node.exc.args) == 0):
                return bool(error_message in {None, ""})
            if type(node.exc.args[0]) is ast.Str:
                return bool(error_message == node.exc.args[0].s)
            if type(node.exc.args[0]) is ast.Num:
                return bool(error_message == node.exc.args[0].n)
        return False

    def cause(cause, node):
        if type(node.cause) is ast.Name:
            return bool(cause == node.cause.id)
        return False

    def __new__(self, node, _error_type, _error_message, _cause,
                consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            if _error_type is not None:
                partial_validators.add(
                    self.error_type(error_type=_error_type, node=node)
                )
            if _error_message is not None:
                partial_validators.add(
                    self.error_message(error_message=_error_message, node=node)
                )
            if _cause is not None:
                partial_validators.add(self.cause(cause=_cause, node=node))
            return all(partial_validators)
        except AttributeError:
            return False


class Yielding(object):
    def regular(node):
        return bool(type(node) is ast.Yield)

    def comprehension(is_sought, node):
        if is_sought:
            return bool(type(node) is ast.GeneratorExp)
        return bool(type(node) is not ast.GeneratorExp)

    def yield_from(is_sought, node):
        if is_sought:
            return bool(type(node) is ast.YieldFrom)
        return bool(type(node) is not ast.YieldFrom)

    def basic(node):
        return bool(
            Yielding.regular(node=node) or
            Yielding.comprehension(is_sought=True, node=node) or
            Yielding.yield_from(is_sought=True, node=node)
        )

    def __new__(self, node, _in_comprehension, _yield_from,
                consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            if _in_comprehension is not None:
                partial_validators.add(
                    self.comprehension(
                        is_sought=bool(_in_comprehension), node=node
                    )
                )
            if _yield_from is not None:
                partial_validators.add(
                    self.yield_from(is_sought=bool(_yield_from), node=node)
                )
            return all(partial_validators)
        except AttributeError:
            return False


class Making_Global(object):
    def basic(node):
        return bool(type(node) is ast.Global)

    def _id_(_id, node):
        return bool(_id in {str(name) for name in node.names})

    def __new__(self, node, _id, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            if _id is not None:
                partial_validators.add(self._id_(_id=_id, node=node))
            return all(partial_validators)
        except AttributeError:
            return False


class Making_Nonlocal(object):
    def basic(node):
        return bool(type(node) is ast.Nonlocal)

    def _id_(_id, node):
        return bool(_id in {str(name) for name in node.names})

    def __new__(self, node, _id, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            if _id is not None:
                partial_validators.add(self._id_(_id=_id, node=node))
            return all(partial_validators)
        except AttributeError:
            return False


class Passing(object):
    def basic(node):
        return bool(type(node) is ast.Pass)

    def __new__(self, node, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            return all(partial_validators)
        except AttributeError:
            return False


class Returning(object):
    def regular(node):
        return bool(type(node) is ast.Return)

    def in_lambda(node):
        return False
        raise NotImplemented

    def basic(node):
        return bool(Returning.regular(node=node) or
                    Returning.in_lambda(node=node))

    def __new__(self, node, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            return all(partial_validators)
        except AttributeError:
            return False


class Breaking(object):
    def basic(node):
        return bool(type(node) is ast.Break)

    def __new__(self, node, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            return all(partial_validators)
        except AttributeError:
            return False


class Continuing(object):
    def basic(node):
        return bool(type(node) is ast.Continue)

    def __new__(self, node, consideration, _knowledge):
        try:
            partial_validators = set([consideration, self.basic(node=node)])
            return all(partial_validators)
        except AttributeError:
            return False
