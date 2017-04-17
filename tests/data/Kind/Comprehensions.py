for i in range(10):
    for y in [str(i) for i in range(10)]:
        print({i: y})

def f(n):
    return {i: str(i) for i in range(n)}


def g(n):
    yield f(n)


h = ({i: str(i)} for i in range(10))

q = (x for x in {"a", "b", "c"} | {i * 2 for i in {"a", "b", "c"}})
