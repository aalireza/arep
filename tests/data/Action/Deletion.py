a = [i for i in range(10)]
del a

def f(a, b):
    return a + b

class Something(object):
    def __init__(self):
        self.spam = {i: (i + 5) for i in range(10)}

    def another_thing(self):
        try:
            del self.spam[0]
        except:
            pass
