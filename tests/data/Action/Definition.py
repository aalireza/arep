def f(x, y):
    return x, y

f()

def g():
    def h():
        return True
    return h

# Lambda assignment is not considered as a definition
x = lambda x: x ** 2

class Test(object):
    def __init__(self):
        pass

class AnotherTest(object):

    class AnotherAnotherTest(type):
        def __init__(self):
            pass

x = 2

class AnotherAnotherAnotherTest(AnotherTest):
    def __init__(self):
        pass
