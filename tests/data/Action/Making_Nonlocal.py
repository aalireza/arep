def f(x):
    def g():
        nonlocal x
        x += 2
        return x
    return g() ** 2


def f(x, y):
    def g():
        nonlocal x
        x += 2
        def h():
            nonlocal y
            y += 3
            return y
        return h()
    g()
    return x + y
