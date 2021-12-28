import numpy as np

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


if __name__ == '__main__':

    val, d = cal_value2(
        rate0=-10,

        rate1=30,
        n1=3,

        rate2=0,
        n2=100,
    )

    print(val)
    print("Discount: {:.2f}%".format(d))

    pe = 100

    log2_pe = np.log(pe) / np.log(2)
    log2_val = np.log(val) / np.log(2) - log2_pe
    print("PE: {}".format(pe))
    print("Log2 PE: {:.2f}".format(log2_pe))
    print("Res: {:.2f}".format(log2_val))



