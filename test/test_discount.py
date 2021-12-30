import numpy as np


class ValueModel:
    def __init__(self, pe, rate, year):
        self.code = ''
        self.name = ''
        self.rate0 = -10
        self.pe = pe
        self.rate = rate
        self.year = year

    @property
    def value(self):
        x, y = cal_value2(
            rate0=self.rate0,
            rate1=self.rate[0],
            n1=self.year[0],
            rate2=self.rate[1],
            n2=self.year[1],
        )

        return x

    def value_k(self, p1, p2):
        x1 = self.value
        x2 = self.pe

        print("Val: {}".format(x1))
        print("PE: {}".format(x2))

        k = x1 / x2

        max_val = -np.inf
        max_a = None
        for a in np.arange(0, 1, 0.01):
            ret = (p1 * np.log((k - 1) * a + 1) + p2 * np.log(1 - a)) / np.log(2)

            if ret > max_val:
                max_val = ret
                max_a = a
        print("Max_Val: {:.2f}".format(max_val))
        print("Max_Percent: {:.0f}%".format(max_a * 100))


def cal_value(a, n):
    res = (a ** n - 1) / (a - 1)
    return res


def sum_value(rate, n=1e7):
    res = cal_value(a=rate, n=n)
    return res


def sum_value2(rate1, rate2, n1, n2):
    res = sum_value(rate1, n1) + (rate1**n1) * sum_value(rate2, n2)
    return res


def cal_value2(rate0, rate1=0, rate2=0, n1=0, n2=0):
    a0 = 1 + rate0/100
    a1t = 1 + rate1/100
    a2t = 1 + rate2/100

    a1 = a0 * a1t
    a2 = a0 * a2t
    res = sum_value2(a1, a2, n1, n2)
    d_percent = 1 / res * 100

    return res, d_percent


def cal_kelly(p1, p2, k):
    max_val = -np.inf
    max_a = None
    for a in np.arange(0, 1, 0.01):
        # print(a)
        ret = (p1 * np.log((k-1)*a + 1) + p2 * np.log(1 - a)) / np.log(2)

        if ret > max_val:
            max_val = ret
            max_a = a
    print("Max_Val: {:.2f}".format(max_val))
    print("Max_Percent: {:.0f}%".format(max_a * 100))


if __name__ == '__main__':
    m = ValueModel(
        pe=20,
        rate=[5, 5],
        year=[5, 30],
    )
    m.value_k(
        p1=0.5,
        p2=0.1,
    )
