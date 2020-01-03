import math


def print_Bezout_identity(n, m):
    assert isinstance(n, int), str(n) + ' is not an integer'
    assert isinstance(m, int), str(m) + ' is not an integer'

    if m == 0:
        print(f'{n} * 1 + {m} * 0 = {n}')
        return 1, 0, n

    old_s, s = 1, 0
    old_t, t = 0, 1
    old_r, r = n, m

    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t

    print(f'{n} * {old_s} + {m} * {old_t} = {old_r}')
    return old_s, old_t, old_r
