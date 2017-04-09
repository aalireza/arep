for x in range(10):
    print(x)

y = 10

f_not_var = lambda x: x ** 4
f_var = (lambda x: x ** 4)(2)


def f(x, y):
    return zip(x[y], y[x])


class Something(object):
    def __init__(self, test):
        self.test == test

    def someMethod(self):
        return self.test


a = Something(2)
print(a.someMethod(), a.test)


class SomethingElse(Something):
    pass
