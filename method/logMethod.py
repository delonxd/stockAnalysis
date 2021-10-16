from functools import wraps
import time


class MainLog:
    content = ''

    def __init__(self):
        pass

    @classmethod
    def init_log(cls):
        cls.content = ''

    @classmethod
    def add_log(cls, log_str):
        row = get_log_time() + log_str
        cls.content = cls.content + row + '\n'
        print(row)


def get_log_time():
    return time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time()))


def log_it(logfile):
    def logging_decorator(func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_str = func.__name__ + " was called"
            MainLog.add_log(log_str)

            res = func(*args, **kwargs)

            log_str = func.__name__ + " was finished"
            MainLog.add_log(log_str)

            return res

        return wrapped_function
    return logging_decorator


def exception_req(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        flag = True
        while flag is True:
            try:
                res = func(*args, **kwargs)
                flag = False
                return res

            except BaseException as e:
                print(e)
                flag = False
                time.sleep(1)
    return wrapped_function


@log_it('')
@exception_req
def test(s):
    print('1' + 1)
    return "res"


if __name__ == '__main__':
    a = test('1111')

    print(a)

    print(MainLog.content)