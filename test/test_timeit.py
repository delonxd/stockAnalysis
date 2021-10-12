import timeit
from timeit import Timer
import datetime as dt


def test1(date0, dict0, list0):
    for key in list0:
        val = dict0.get(key)


def test2(date0, dict0, list0):
    for key in list0:
        val = key * 2 / 2
        date = date0 + dt.timedelta(days=key)


if __name__ == '__main__':
    str2 = """
from __main__ import test1
from __main__ import test2
import datetime as dt
import random

px = list(range(2000))
date0 = dt.date(2018, 7, 20)
px_dict = dict()
for i in px:
    date = date0 + dt.timedelta(days=i)
    px_dict[i] = date
list0 = [random.randint(0, 1999) for _ in range(100)]

    """


    t1 = Timer("test1(date0, px_dict, list0)", str2)
    t2 = Timer("test2(date0, px_dict, list0)", str2)
    print(t1.timeit(1000))
    print(t2.timeit(1000))
