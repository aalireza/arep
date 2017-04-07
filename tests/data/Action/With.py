with open('Call.py', 'r') as f:
    call_program = f.read()

def f():
    def g():
        return True
    with g():
        print(True)
