from arep.Validators.forms import ValidationForm, ValidatorForm
from arep.Validators import action
from arep.utils import ast_operation_symbols
import ast

"""
The validations for Grepping of all Kind constraint types are in this file.

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

    def arity(arity, node, knowledge):
        # For a proper implementation, one needs to remember function
        # redefentions.
        raise NotImplementedError

    def return_type(return_type, node, knowledge):
        # For a proper implementation, one needs to remember function
        # redefenitions to properly map function calls to their
        # definitions.
        raise NotImplementedError

    def name(name, node, knowledge):
        if name is None:
            return True
        if (
                Functions.basic(node, True, knowledge) and
                Functions.Lambda.basic(node, False, knowledge)
        ):
            return ValidationForm(
                name,
                condition=bool(name == (
                    node.name if Functions._regular_def(node, knowledge)
                    else node.id if Functions._regular_call(node, knowledge)
                    else not name))
            )
        if (
                Functions.Lambda.basic(node, True, knowledge) and
                Functions.Lambda.immediately_called(False, node, knowledge) and
                bool(type(node._parent) is ast.Assign)
        ):
            return ValidationForm(
                name,
                condition=bool(name in [
                    target.id for target in node._parent.targets
                ])
            )
        return not name

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

    class Parameters(object):

        def _has_fixed_arguments(node, knowledge):
            if node.lineno == 29 and node.col_offset == 16:
                print(node)
            if any([f(node, knowledge) for f in {
                    Functions._regular_def, Functions._lambda}]):
                return bool(len(node.args.args) > 0)
            if Functions._regular_call(node, knowledge):
                return bool(len(node._parent.args) > 0
                            if hasattr(node._parent, "args")
                            else False)

        def _has_variadic_arguments(node, knowledge):
            if any([f(node, knowledge) for f in {
                    Functions._regular_def, Functions._lambda}]):
                return bool(node.args.vararg is not None)

        def _has_fixed_keywords(node, knowledge):
            if any([f(node, knowledge) for f in {
                    Functions._regular_def, Functions._lambda}]):
                return bool(len(node.args.defaults) > 0)
            if Functions._regular_call(node, knowledge):
                return bool(len(node._parent.keywords) > 0
                            if hasattr(node._parent, "keywords")
                            else False)

        def _has_variadic_keywords(node, knowledge):
            if any([f(node, knowledge) for f in {
                    Functions._regular_def, Functions._lambda}]):
                return bool(node.args.kwarg is not None)

        def basic(node, consideration, knowledge):
            if consideration is None:
                return True
            if Functions.basic(node, True, knowledge):
                return ValidationForm(
                    consideration,
                    condition=bool(any([
                        getattr(Functions.Parameters, f)(node, knowledge)
                        for f in {"_has_fixed_arguments",
                                  "_has_fixed_keywords",
                                  "_has_variadic_arguments",
                                  "_has_variadic_keywords"}
                    ]))
                )
            return not consideration

        def with_default_values(with_default_values, node, knowledge):
            if with_default_values is None:
                return True
            if (
                    Functions.Parameters.basic(node, True, knowledge) and
                    not Functions._regular_call(node, knowledge)
            ):
                return ValidationForm(
                    with_default_values,
                    condition=bool(len(node.args.defaults) > 0)
                )
            return not with_default_values

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

        class Arguments(object):
            def basic(node, consideration, knowledge):
                if consideration is None:
                    return True
                if Functions.basic(node, True, knowledge):
                    return ValidationForm(
                        consideration,
                        condition=bool(any([
                            getattr(Functions.Parameters, f)(node, knowledge)
                            for f in {"_has_fixed_arguments",
                                      "_has_variadic_arguments"}
                        ]))
                    )
                return not consideration

            def is_variadic(is_variadic, node, knowledge):
                if is_variadic is None:
                    return True
                if Functions.Parameters.Arguments.basic(node, True, knowledge):
                    return ValidationForm(
                        is_variadic,
                        condition=bool(
                            Functions.Parameters._has_variadic_arguments(
                                node, knowledge)
                        )
                    )
                return not is_variadic

            def __new__(self, **kwargs):
                return ValidatorForm(self, **kwargs)

        class Keywords(object):
            def basic(node, consideration, knowledge):
                if consideration is None:
                    return True
                if Functions.basic(node, True, knowledge):
                    return ValidationForm(
                        consideration,
                        condition=bool(any([
                            getattr(Functions.Parameters, f)(node, knowledge)
                            for f in {"_has_fixed_keywords",
                                      "_has_variadic_keywords"}
                        ]))
                    )
                return not consideration

            def is_variadic(is_variadic, node, knowledge):
                if is_variadic is None:
                    return True
                if Functions.Parameters.Keywords.basic(node, True, knowledge):
                    return ValidationForm(
                        is_variadic,
                        condition=bool(
                            Functions.Parameters._has_variadic_keywords(
                                node, knowledge)
                        )
                    )
                return not is_variadic

            def __new__(self, **kwargs):
                return ValidatorForm(self, **kwargs)


class Classes(object):
    def _regular_def(node):
        return bool(type(node) is ast.ClassDef)

    def _regular_call(node, knowledge):
        if bool(type(node._parent) is ast.Call):
            return bool(
                getattr(node, "id") in knowledge['Class']
                if hasattr(node, "id") else False
            )
        return False

    def _name_def(node):
        return (node.name if bool(type(node) is ast.ClassDef) else False)

    def _name_call(node, knowledge):
        return (getattr(node, "id") if hasattr(node, "id") else False)

    def basic(node, consideration, knowledge):
        return ValidationForm(
            consideration,
            condition=bool(
                Classes._regular_def(node) or
                Classes._regular_call(node, knowledge)
            )
        )

    def name(name, node, knowledge):
        if name is None:
            return True
        if Classes.basic(node, True, knowledge):
            return ValidationForm(
                name,
                condition=bool(
                    (name == Classes._name_def(node))
                    if Classes._regular_def(node)
                    else (name == Classes._name_call(node, knowledge))
                    if Classes._regular_call(node, knowledge)
                    else (not name)
                )
            )
        return not name

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Comprehensions(object):
    def basic(node, consideration, knowledge):
        return ValidationForm(
            consideration,
            condition=bool(type(node) in knowledge['comprehension_forms'])
        )

    def of_list(of_list, node):
        return ValidationForm(
            of_list,
            condition=bool(type(node) is ast.ListComp)
        )

    def of_set(of_set, node):
        return ValidationForm(
            of_set,
            condition=bool(type(node) is ast.SetComp)
        )

    def of_dict(of_dict, node):
        return ValidationForm(
            of_dict,
            condition=bool(type(node) is ast.DictComp)
        )

    def of_gen(of_gen, node):
        return ValidationForm(
            of_gen,
            condition=bool(type(node) is ast.GeneratorExp)
        )

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)


class Operations(object):
    def basic(node, consideration):
        return ValidationForm(
            consideration,
            condition=bool(type(node) in {
                    ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp,
                    ast.AugAssign
            })
        )

    def symbol(symbol, node):
        if symbol is None:
            return True
        if any([getattr(Operations, x)(True, node)
                for x in {'augments_an_assignment', 'is_binary', 'is_unary',
                          'is_boolean'}]):
            return ValidationForm(
                symbol,
                condition=bool(
                    ast_operation_symbols()[type(node.op)] == symbol
                )
            )
        elif Operations.is_comparative(True, node):
            return ValidationForm(
                symbol,
                condition=bool(
                    symbol in {ast_operation_symbols()[type(op)]
                               for op in node.ops}
                )
            )
        return not symbol

    def augments_an_assignment(augments_an_assignment, node):
        if augments_an_assignment is None:
            return True
        if Operations.basic(node, True):
            return ValidationForm(
                augments_an_assignment,
                condition=bool(type(node) is ast.AugAssign)
            )
        return not augments_an_assignment

    def is_boolean(is_boolean, node):
        if is_boolean is None:
            return True
        if Operations.basic(node, True):
            return ValidationForm(
                is_boolean,
                condition=bool(type(node) is ast.BoolOp)
            )
        return not is_boolean

    def is_comparative(is_comparative, node):
        if is_comparative is None:
            return True
        if Operations.basic(node, True):
            return ValidationForm(
                is_comparative,
                condition=bool(type(node) is ast.Compare)
            )
        return not is_comparative

    def is_unary(is_unary, node):
        if is_unary is None:
            return True
        if Operations.basic(node, True):
            return ValidationForm(
                is_unary,
                condition=bool(type(node) is ast.UnaryOp)
            )
        return not is_unary

    def is_binary(is_binary, node):
        if is_binary is None:
            return True
        if Operations.basic(node, True):
            return ValidationForm(
                is_binary,
                condition=bool(type(node) is ast.BinOp)
            )
        return not is_binary

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)
