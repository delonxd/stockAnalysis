from functools import wraps
import time
import datetime as dt


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

    @classmethod
    def add_log_accurate(cls, log_str):
        row = get_log_time_accurate() + log_str
        cls.content = cls.content + row + '\n'
        print(row)

    @classmethod
    def add_split(cls, txt):
        row = txt * 100
        cls.content = cls.content + row + '\n'
        print(row)

    @classmethod
    def add_empty(cls):
        row = '\n'
        cls.content = cls.content + row + '\n'
        print(row)

    @classmethod
    def write(cls, path, init=False):
        cls.add_log('save log --> %s' % path)
        with open(path, "w", encoding='utf-8') as f:
            f.write(cls.content)
        if init is True:
            cls.init_log()

    @classmethod
    def write_add(cls, path):
        flag = True
        while flag:
            try:
                with open(path, "a", encoding='utf-8') as f:
                    f.write(cls.content)
                flag = False
            except Exception as e:
                log_str = '\n%s\n' % e
                cls.add_log(log_str)


def get_log_time():
    return time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time()))


def get_log_time_accurate():
    return '%s  ' % dt.datetime.now()


def log_it(logfile):
    def logging_decorator(func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_str = func.__name__ + " was called..."
            MainLog.add_log(log_str)

            res = func(*args, **kwargs)

            log_str = func.__name__ + " complete."
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