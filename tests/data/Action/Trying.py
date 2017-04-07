x = list()
try:
    x.pop()
except IndexError("Something"):
    pass

try:
    x.pop()
except IndexError as e:
    print(e)
except AttributeError:
    print("False")
finally:
    print("Here")

def f(x, y):
    try:
        return x + y
    except Exception("Test"):
        pass
