a = range(10)[0]

b = [i for i in range(10)][:-1]

print("Spam")

c = b + [a]

jump = c[::2]

def f(x):
    print([a, b, c, jump][x])
