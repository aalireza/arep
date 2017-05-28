from arep.Validators.forms import (
    ValidationForm, ValidatorForm, PositionalBasicForm
)

"""
The validations for Grepping of all Properties constraint types are in this
file.

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


class Positional(object):
    class Line_Numbers(object):
        def basic(consideration, minimum, maximum):
            return PositionalBasicForm(consideration, minimum, maximum)

        def minimum(minimum, node):
            return ValidationForm(
                (minimum is not False),
                condition=bool(minimum <= node.lineno)
            )

        def maximum(maximum, node):
            return ValidationForm(
                (maximum is not False),
                condition=bool(node.lineno <= maximum)
            )

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

    class Column_Numbers(object):
        def basic(consideration, minimum, maximum):
            return PositionalBasicForm(consideration, minimum, maximum)

        def minimum(minimum, node):
            return ValidationForm(
                (minimum is not False),
                condition=bool(minimum <= node.col_offset)
            )

        def maximum(maximum, node):
            return ValidationForm(
                (maximum is not False),
                condition=bool(node.col_offset <= maximum)
            )

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)
