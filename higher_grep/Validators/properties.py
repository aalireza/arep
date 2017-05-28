from higher_grep.Validators.forms import (
    ValidationForm, ValidatorForm, PositionalBasicForm
)


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
