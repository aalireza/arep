from higher_grep.Validators.forms import ValidationForm, ValidatorForm


class Positional(object):
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


class Cohesiveness(object):
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


class Nestedness(object):
    def basic(node, consideration):
        raise NotImplementedError

    def minimum(minimum, node):
        raise NotImplementedError

    def maximum(maximum, node):
        raise NotImplementedError
