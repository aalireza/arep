def f(*args, **kwargs):
    return (lambda arglist, kwarglist: zip(arglist, kwarglist.keys()))(
        *args, **kwargs
    )

a = [1, 2, 3, 4]

def g(q, w, e, r):
    return sum([q, w, e, r])

print(g(*a))

x = range(10)

p, *q, r = x

mapping = {i: str(i) for i in range(10)}

def h(**kwargs):
    return sum(kwargs.keys())

x = h(**mapping)

