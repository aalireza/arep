x = 2

global x

def f(y):
    global x
    x += y
    return x
