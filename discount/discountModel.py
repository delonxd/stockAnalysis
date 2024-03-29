import numpy as np
import matplotlib.pyplot as plt


class ValueModel:
    def __init__(self, pe, rate, year, rate0=-10):
        self.code = ''
        self.name = ''
        self.rate0 = rate0
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

    def remain_value(self, nr, rr):
        x = cal_remain_value(
            rate0=self.rate0,
            rate1=self.rate[0],
            n1=self.year[0],
            rate2=self.rate[1],
            n2=self.year[1],
            nr=nr,
            rr=rr,
        )

        return x

    def show_value(self):
        print("r1: {:.2f}%, Val: {:.3f}".format(self.rate[0], self.value))

    def value_k(self, p1, p2):
        x1 = self.value
        x2 = self.pe
        k = x1 / x2 * 0.75

        print("Val: {}".format(x1))
        print("PE: {}".format(x2))
        print("K: {}\n".format(k))

        max_val = -np.inf
        max_a = None
        for a in np.arange(0, 1, 0.001):
            ret = (p1 * np.log((k - 1) * a + 1) + p2 * np.log(1 - a)) / np.log(2)

            if ret > max_val:
                max_val = ret
                max_a = a
        print("Max_Val: {:.3f}".format(max_val))
        print("Max_Percent: {:.1f}%\n".format(max_a * 100))


class ValueModel2:
    def __init__(self, rate, year, rate0, asset, profit, r_ratio):
        self.code = ''
        self.name = ''
        self.asset = asset
        self.profit = profit

        self.rate0 = rate0

        self.rate = rate
        self.year = year

        self.r_ratio = r_ratio / 100

        self.sq = list(zip(self.rate, self.year))

    @property
    def value(self):
        sq = self.sq.copy()
        _, x = sum_profit(self.profit, sq, self.rate0)
        ret = x + self.asset
        return ret

    @property
    def value_reserved(self):
        sq = self.sq.copy()
        _, x = sum_profit(self.profit, sq, 0)
        year = sum(self.year)
        r = 1 - self.rate0 / 100
        x = x + self.asset
        ret = x * (r ** year)
        return ret

    @property
    def value_average(self):
        ret = self.value * self.r_ratio + self.value_reserved * (1 - self.r_ratio)
        return ret

    def sum_profit(self, ini):
        sq = self.sq.copy()
        return sum_profit(ini, sq, self.rate0)

    def split_sq(self, t):
        ret = []
        counter = 0
        for rate, year in self.sq:
            if counter + year >= t:
                ret.append((rate, t-counter))
                break
            counter += year
            ret.append((rate, year))
        return ret

    def iter_sum(self):
        ret = []
        profit = self.profit
        asset = self.asset
        total = sum_profit(1, self.sq.copy(), self.rate0)[1]
        r0 = 1 / (1 + self.rate0 / 100)
        for t in range(50):
            sub_sq = self.split_sq(t)

            r1, val1 = sum_profit(1, sub_sq, self.rate0)
            r2, val2 = sum_profit(1, sub_sq, 0)
            s1 = ((profit * val2) + asset) * (r0 ** t)
            s2 = profit * (total - val1)
            ret.append(s1 + s2)
        return ret

    @staticmethod
    def iter_return(value, mkv, year: int):
        val = value / mkv
        ret = []
        for t in range(1, year+1):
            tmp = (val ** (1/t)-1) * 100
            ret.append(tmp)
        return ret

    # def iter_sum2(self):
    #     ret = []
    #     profit = self.profit
    #     asset = self.asset
    #     total = sum_profit(1, self.sq.copy(), self.rate0)[1]
    #     r0 = 1 / (1 + self.rate0 / 100)
    #
    #     for t in range(50):
    #         val1 =


def sum_profit(ini, sq, adj):
    if len(sq) == 0:
        return ini, 0
    else:
        rate, year = sq.pop(0)
        r1 = 1 + rate / 100
        r2 = 1 - adj / 100
        r0 = r1 * r2
        t1 = cal_value(r0, year) * ini
        if ini == 0 or r0 ** year == 0:
            ini2 = 0
        else:
            ini2 = ini * (r0 ** year)
        last, t2 = sum_profit(ini2, sq, adj)
        t = t1 + t2
        return last, t


def cal_value(a, n):
    if a == 1:
        res = n
    else:
        res = (a ** n - 1) / (a - 1)
    return res


def sum_value(rate, n=1e7):
    res = cal_value(a=rate, n=n)
    return res


def sum_value2(a0, a1, a2, n1, n2, n3):
    res = sum_value(a1, n1) + (a1**n1) * sum_value(a2, n2) + (a1**n1) * (a2**n2) * sum_value(a0, n3)
    return res


def cal_value2(rate0, rate1=0, rate2=0, n1=0, n2=0):
    n3 = 1e7 - n1 - n2

    a0 = 1 + rate0/100
    a1t = 1 + rate1/100
    a2t = 1 + rate2/100

    a1 = a0 * a1t
    a2 = a0 * a2t
    res = sum_value2(a0, a1, a2, n1, n2, n3)
    d_percent = 1 / res * 100

    return res, d_percent


def cal_remain_value(rate0, rate1=0, rate2=0, n1=0, n2=0, nr=30, rr=0.4):
    n3 = 1e7 - n1 - n2

    if nr <= n1:
        n1b = nr
        n2b = 0
        n3b = 0
    elif nr <= n1 + n2:
        n1b = n1
        n2b = nr - n1
        n3b = 0
    elif nr <= n1 + n2 + n3:
        n1b = n1
        n2b = n2
        n3b = nr - n1 - n2
    else:
        n1b = n1
        n2b = n2
        n3b = n3

    a0 = 1 + rate0/100
    a1t = 1 + rate1/100
    a2t = 1 + rate2/100

    a1 = a0 * a1t
    a2 = a0 * a2t

    res0 = sum_value2(a0, a1, a2, n1, n2, n3)
    res1_real = sum_value2(a0, a1, a2, n1b, n2b, n3b)
    res2_real = res0 - res1_real

    res1_book = sum_value2(1, a1t, a2t, n1b, n2b, n3b)
    res1_remain = res1_book * (a0**nr)

    # res_plus = res1_remain + res2_real

    remain_rate = rr
    res_plus = res1_real * (1 - remain_rate) + res1_remain * remain_rate + res2_real

    # print("Value: {:.2f}".format(res0))
    # print("Remain: {:.2f}".format(res1_remain))
    # print("Left: {:.2f}".format(res2_real))
    # print("Value2: {:.2f}".format(res_plus))
    p = res_plus / res0 * 100
    print("nr: {:.0f}, Value2: {:.2f}, percent: {:.2f}%".format(nr, res_plus, p))
    print("Value: {:.2f}".format(res0))

    # return res0, res1_remain, res2_real
    return p


def cal_kelly(p1, p2, k):
    max_val = -np.inf
    max_a = None
    for a in np.arange(0, 1, 0.001):
        # print(a)
        ret = (p1 * np.log((k-1)*a + 1) + p2 * np.log(1 - a)) / np.log(2)

        if ret > max_val:
            max_val = ret
            max_a = a
    print("Max_Val: {:.2f}".format(max_val))
    print("Max_Percent: {:.0f}%".format(max_a * 100))


def get_index(list0, val):
    res = 0
    for index, x in enumerate(list0):
        if val <= x:
            res = index
            break
    if val > list0[-1]:
        res = len(list0)
    return res


def test_value():
    v_list = []
    for r1 in np.arange(-10, 50.01, 0.01):
        if r1 <= 5:
            r2 = r1
        else:
            r2 = 5
        m = ValueModel(
            pe=10,
            rate=[r1, r2],
            year=[10, 10],
            rate0=-10,
        )

        v_list.append(m.value/2)
        m.show_value()


def test_remain_rate():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(16, 9), dpi=90)

    fig_tittle = 'Distribution'

    fig.suptitle(fig_tittle)
    fig.subplots_adjust(hspace=0.3)

    ax1 = fig.add_subplot(1, 1, 1)

    m1 = ValueModel(
        pe=10,
        rate=[20, 10],
        year=[10, 10],
        rate0=-10,
    )

    ax1.yaxis.grid(True, which='both')
    ax1.xaxis.grid(True, which='both')

    for i in range(11):
        rr = i / 10
        yy = []
        for nr in range(100):
            tmp = m1.remain_value(nr, rr)
            yy.append(tmp)

        xx = range(100)
        ax1.plot(xx, yy, linestyle='-', alpha=0.8, color='r', label=str(i))

    ax1.legend()
    ax1.set_ylim([0, 105])

    plt.show()


if __name__ == '__main__':
    # test_remain_rate()
    m1 = ValueModel2([15, 10, 0], [10, 10, np.inf], 10, 120, 10)
    # res = m1.value
    res = m1.iter_return(2000, 50)
    print(res)
    # res = sum_profit(1, [(0, 0), (0, np.inf)], -10)
    # print(res)