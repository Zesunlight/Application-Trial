import math


def normal_distribution(x, mu=0, sigma=1):
    return 1 / (sigma * math.sqrt(2 * math.pi)) * math.exp(-(x - mu)**2 / (2 * sigma**2))


def simpson_integral(a, b, n, mu=0, sigma=1):
    """
    辛普森积分法
    :param a: 上限
    :param b: 下限
    :param n: 区间等分成 n 段
    :param mu: 均值
    :param sigma: 方差
    :return: 积分近似值
    """
    slide = (b - a) / n  # 步长
    result = 0
    left_y, right_y = normal_distribution(a, mu, sigma), 0
    for x in range(n):
        right_y = normal_distribution(a + (x + 1) * slide, mu, sigma)
        mid_y = normal_distribution(a + (x + 1 / 2) * slide, mu, sigma)
        result += (left_y + 4 * mid_y + right_y) * slide / 6
        left_y = right_y

    return result


def taylor_integral(a, b, k=50, mu=0, sigma=1):
    """
    泰勒展开近似。上下限过大的时候（大概绝对值大于6）计算失真，可能是存储精度的原因
    :param a: 下限
    :param b: 上限
    :param k: 取泰勒展开的前 k 项
    :param mu: 均值
    :param sigma: 方差
    :return: 积分近似值
    """
    left_preimage, right_preimage = 0, 0
    left_coefficient, right_coefficient = a - mu, b - mu

    for i in range(k):
        left_preimage += left_coefficient / (2 * i + 1)
        right_preimage += right_coefficient / (2 * i + 1)

        left_coefficient *= -1 / (i + 1) / (2 * sigma**2) * (a - mu)**2
        right_coefficient *= -1 / (i + 1) / (2 * sigma**2) * (b - mu)**2

    return (right_preimage - left_preimage) / (sigma * math.sqrt(2 * math.pi))


def trapezoid_integral(a: int, b: int, n: int, mu=0, sigma=1) -> float:
    """
    梯形面积近似
    :param a: 上限
    :param b: 下限
    :param n: 区间等分成 n 段
    :param mu: 均值
    :param sigma: 方差
    :return: 积分近似值
    """
    slide = (b - a) / n  # 步长
    result = 0
    left_y, right_y = normal_distribution(a, mu, sigma), 0
    for x in range(n):
        right_y = normal_distribution(a + (x + 1) * slide, mu, sigma)
        result += (left_y + right_y) * slide / 2
        left_y = right_y

    return result


if __name__ == '__main__':
    print(trapezoid_integral(-7, 0, 10**4))
    print(simpson_integral(-6, 0, 10**4))
    print(taylor_integral(-6, 0))
