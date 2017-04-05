assert 2 > 1
assert 1 < 2, "test"

def f(x):
    assert x > 2, "nested test"
    return x
