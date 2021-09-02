
from scipy.special import perm
from scipy.special import comb



def func1(n, num, time, flag):
    if flag == '先手':
        time = 8 + time
    elif flag == '后手':
        time = 10 + time

    print(time)
    a = 39
    b = a - num
    c = time - n
    ans = comb(num, n) * comb(b, c) / comb(a, time)
    return ans

def func2(n, num, time, flag):
    l = list(range(n))
    ans = 0
    for i in l:
        a = func1(i, num, time, flag)
        ans += a
    ans = 1 - ans
    return ans


# d = func1(0, 9, 10)
aa = 1
bb = 6
r = 1

print(func2(aa, bb, r, '先手'))
print(func2(aa, bb, r, '后手'))

# print(func2(aa, bb, r, '后手'))
# print(func2(aa, bb, r, '后手'))
# print(func2(aa, bb, r, '后手'))
