import math


def is_prime(number):
    assert isinstance(number, int), str(number) + ' is not an integer'
    assert number > 1, 'Input must be larger than 1'
    if number % 2 == 0 and number > 2:
        return False
    return all(number % i for i in range(3, int(math.sqrt(number)) + 1, 2))

def is_odd(number):
    assert isinstance(number, int), str(number) + ' is not an integer'
    return bool(number % 2)

def is_even(number):
    assert isinstance(number, int), str(number) + ' is not an integer'
    return not (number % 2)
