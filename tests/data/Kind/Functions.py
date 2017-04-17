def f(x, y):
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
b = NotFunction(f("another stuff"))
