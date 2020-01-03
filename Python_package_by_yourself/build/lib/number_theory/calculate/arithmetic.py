import math


def modular(n, m):
    assert isinstance(n, int), str(n) + ' is not an integer'
    assert isinstance(m, int), str(m) + ' is not an integer'

    return int(math.fmod(n, m))

def remainder(n, m):
    assert isinstance(n, int), str(n) + ' is not an integer'
    assert isinstance(m, int), str(m) + ' is not an integer'

    return n % m

def quotient(n, m):
    assert isinstance(n, int), str(n) + ' is not an integer'
    assert isinstance(m, int), str(m) + ' is not an integer'

    return n // m
