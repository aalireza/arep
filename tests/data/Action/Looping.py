for i in range(10):
    for j in range(i):
        j += i

x = (lambda x: x ** 2)(5)

def f(x):
    for i in x:
        print(i)

a = {i: j for i, j in zip(range(10), range(10))}

b = [x ** 2 for x in range(10)]

for i in range(10):
    if i > 10:
        print("Seriously?")
else:
    print("stuff")

while True:
    for i in range(10):
        if i == 5:
            break
    break
x = 0
while 2 < 1:
    x += 1
    if x > 10:
        break

y = 0
while y < 10:
    while "a" < "b":
        break
    print(y)
    y += 1

while 0:
    while 1:
        raise Exception
