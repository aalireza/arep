x = 2
if x == 2:
    print(True)
elif x > 2:
    print(False)
elif x < 2:
    print(False)
else:
    print(None)

y = (x if 1 > 2 else x + 1)

if type(y) is int:
    print(2)
elif type(y) is str:
    print("y")

genexp = (y for y in range(10) if y % 2 == 0)

dictcomp = {i: j for i, j in zip(range(10), range(10, 20)) if i + j == 12}

nestedlistcomp = [
    x for x in [i for i in range(10) if i % 2 != 0] if x ** 2 > x
]

def f(x):
    return x ** (0.3)

def g(x, func):
    if x != 0:
        return -1 * func(x)

print(g(3, f))
