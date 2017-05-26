from higher_grep.Validators.forms import ValidationForm, ValidatorForm


def _range_checker(minimum, maximum):
    return (
        True
        if not (type(minimum) is type(maximum) is int)
        else bool(minimum <= maximum)
    )


class Positional(object):
    class Line_Numbers(object):
        def basic(node, consideration, minimum, maximum):
            return ValidationForm(
                consideration,
                condition=bool(_range_checker(minimum, maximum))
            )

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
        def basic(node, consideration, minimum, maximum):
            return ValidationForm(
                consideration,
                condition=bool(_range_checker(minimum, maximum))
            )

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


class Nestedness(object):
    class Inward(object):
        def basic(node, consideration):
            raise NotImplementedError

        def minimum(minimum, node):
            raise NotImplementedError

        def maximum(maximum, node):
            raise NotImplementedError

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)

    class Outward(object):
        def basic(node, consideration):
            raise NotImplementedError

        def minimum(minimum, node):
            raise NotImplementedError

        def maximum(maximum, node):
            raise NotImplementedError

        def __new__(self, **kwargs):
            return ValidatorForm(self, **kwargs)
