def f(x, y=0):
    return x + y

def g(x):
    def f(y):
        if y == 0:
            return 0
        return f(g(y-1))
    return x / 2

l = lambda x, y: x ** y

for i in map(lambda x: x ** 2, range(10)):
    print((lambda x: x / 2)(i))


class NotFunction(object):
    b = lambda x: x

    def __init__(self, spam):
        self.spam = spam

    @property
    def ConsideredNotFunction(self):
        return 2


a = NotFunction("stuff")
b = NotFunction(f(x="another stuff"))


def func_without_argument():
    return (lambda: None)


def variadic1(*args):
    def variadic2(*args, **kwargs):
        return sum(args) + sum(kwargs.values())
    return sum(args) + (lambda *args: sum(args))(*args)
