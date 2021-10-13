import timeit
from timeit import Timer
import datetime as dt
import numpy as np
import random
from collections import defaultdict


def test1(date0, dict0, list0):
    res_list = []
    for key in list0:
        val = dict0.get(key)
        res_list.append(val)


def test2(date0, dict0, list0):
    val = np.log2((list0 + 1) * 2323.131 / 16757.252)


def test3(date0, index_list):
    len0 = len(index_list)
    # print('len:', len0)
    # res = []
    px_dict = defaultdict(float)
    bb = np.zeros(len0, dtype='int64')
    for i, index in enumerate(index_list):
        date = dt.datetime.strptime(index, "%Y-%m-%d").date()
        offset = (date - date0).days
        bb[i] = offset
        # res.append(offset)
        # print(offset)
    # aa = np.array(res, dtype='int64')


if __name__ == '__main__':
    str2 = """
from __main__ import test1
from __main__ import test2
from __main__ import test3
import datetime as dt
import random
import numpy as np
from collections import defaultdict

px = list(range(2000))
date0 = dt.date(2018, 7, 20)
px_dict = defaultdict(float)
index_list = []
for i in px:
    date = date0 + dt.timedelta(days=random.randint(1, 1999))
    index = date.strftime("%Y-%m-%d")
    index_list.append(index)
    date0 = date0
#     dt.datetime.strptime(tup[0], "%Y-%m-%d")
# list0 = np.array([random.randint(0, 1999) for _ in range(1000)])

    """

    # t1 = Timer("test1(date0, px_dict, list0)", str2)
    # t2 = Timer("test2(date0, px_dict, list0)", str2)
    # print(t1.timeit(100))
    # print(t2.timeit(100))
    tmp = np.zeros(10, dtype='int64')
    print(tmp.shape[0])
    t3 = Timer("test3(date0, index_list)", str2)
    print(t3.timeit(1))