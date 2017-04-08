while True:
    break

for i in range(10):
    if i > 10:
        break

def f(i):
    while i:
        try:
            "a" + 2
        except:
            continue
        finally:
            break
