def f(x, y):
    def g(a, b):
        return a + b

    return x - y % g(y, x)

print(f(2, 3))

class Stuff(object):
    def __init__(self):
        self.a = 0

a = Stuff()

a.a += a.a + 1
