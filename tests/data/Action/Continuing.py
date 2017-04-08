for i in {"a", 2, True}:
    try:
        i + "a"
    except:
        continue

for i in range(10):
    if i % 2:
        continue
    else:
        print(i)
