
def square(x):
    return x ** 2


def map_square(iter0):
    return map(square, iter0)


def add(x, y):
    return x + y


if __name__ == '__main__':
    res = map(add, map_square([1, 2, 3, 4, 5]), [2])
    print(list(res))