print(int(2))

x = 2
try:
    x + "a"
except:
    x = str(x) + "a"
finally:
    if type(x) == str:
        print(True)
    else:
        print(None)
