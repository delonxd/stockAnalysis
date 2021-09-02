list1 = list(range(0, 10))
a = 0.3
b = 1
c = 0
for i in list1:
    c = b
    b = (1-a) ** i
    print('%.4f, %.4f,' % ((c-b)*8, b))
