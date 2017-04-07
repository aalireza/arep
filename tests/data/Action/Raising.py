def f(x):
    if x > 1:
        raise Exception("Something")
    else:
        raise TypeError

try:
    "a" + 2
except TypeError as e:
    raise Exception("test") from e

raise SystemExit
