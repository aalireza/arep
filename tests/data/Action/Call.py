def f(x, y):
    return (x + y)

x = f()
print(x)
print(f())

def g(x, y):
    return abs(f(x, y))

class Test(object):
    def __init__(self, string):
        self.string = string

b = Test("stuff")
