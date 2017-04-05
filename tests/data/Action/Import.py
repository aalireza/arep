import math
from subprocess import Popen as popen
from ast import parse
import pickle as cpickle

def f(x, y):
    return (x + y)


import os

print(f())

def g(x, y):
    import sys
    return abs(f(x,y))
