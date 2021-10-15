from functools import wraps
import time


def log_it(logfile):
    def logging_decorator(func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

            log_string = func.__name__ + " was called"
            print(start_time, log_string)

            print(args)
            print(kwargs)
            # with open(logfile, 'a') as opened_file:
            #     opened_file.write(log_string + '\n')
            # print(logfile)
            res = func(*args, **kwargs)

            return res

        return wrapped_function
    return logging_decorator


@log_it('asaada')
def test(stock_code):
    print(1 + 1)
    return "res"


if __name__ == '__main__':
    a = test('1111')

    print(a)