from higher_grep.Validators import ValidationForm, ValidatorForm


class Positional(object):
    def basic(node, consideration):
        raise NotImplementedError

    def __new__(self, **kwargs):
        return ValidatorForm(self, **kwargs)

    class Line_Numbers(object):
        def basic(node, consideration):
            raise NotImplementedError

        def minimum(minimum, node):
            raise NotImplementedError

        def maximum(maximum, node):
            raise NotImplementedError

        def __new__(self, **kwargs):
            raise NotImplementedError

    class Column_Numbers(object):
        def basic(node, consideration):
            raise NotImplementedError

        def minimum(minimum, node):
            raise NotImplementedError

        def maximum(maximum, node):
            raise NotImplementedError

        def __new__(self, **kwargs):
            raise NotImplementedError
