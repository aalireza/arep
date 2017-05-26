def f(x, y):
    return x + y

class Temp(object):
    def __init__(self, arg):
        self.y = arg


class Test(object):
    class T1(object):
        def __init__(self, arg):
            self.a = Temp(arg)

    def __init__(self):
        self.x = False

    def SomeMethod(self, x):
        return x ** 2

    def Func(y):
        return y - 2

print(Test.Func(2))
a = Test()
a.SomeMethod(2)
