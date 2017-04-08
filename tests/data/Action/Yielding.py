x = 2

g = (x for x in range(10))


def f(l):
    for i in range(l):
        yield i ** 2


def ff(f):
    yield from f


print("Noise")
