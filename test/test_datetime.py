"""
%y 两位数的年份表示（00-99）
%Y 四位数的年份表示（000-9999）
%m 月份（01-12）
%d 月内中的一天（0-31）
%H 24小时制小时数（0-23）
%I 12小时制小时数（01-12）
%M 分钟数（00-59）
%S 秒（00-59）
%a 本地简化星期名称
%A 本地完整星期名称
%b 本地简化的月份名称
%B 本地完整的月份名称
%c 本地相应的日期表示和时间表示
%j 年内的一天（001-366）
%p 本地A.M.或P.M.的等价符
%U 一年中的星期数（00-53）星期天为星期的开始
%w 星期（0-6），星期天为星期的开始
%W 一年中的星期数（00-53）星期一为星期的开始
%x 本地相应的日期表示
%X 本地相应的时间表示
%Z 当前时区的名称
%% %号本身
"""

import time
import datetime as dt


def show_var(name, var):
    print('%s: %s' % (name, var))
    print('%s type: %s' % (name, type(var)))
    print('')


if __name__ == '__main__':

    print(dt.datetime.now())
    # 得到 str类型
    time_str = '2018-05-22 08:30:00'
    show_var('time_str', time_str)

    # str类型 转换 struct_time类型
    struct_time1 = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    show_var('struct_time1', struct_time1)

    # struct_time类型 转换 timestamp类型
    timestamp1 = time.mktime(struct_time1)
    show_var('timestamp1', timestamp1)

    # 得到 timestamp类型
    timestamp2 = time.time()
    show_var('timestamp2', timestamp2)

    # timestamp类型 转换 struct_time类型
    struct_time = time.localtime(timestamp2)
    show_var('struct_time', struct_time)

    # struct_time类型 转换 str类型
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)
    show_var('time_str', time_str)

    ##################################################################

    # 得到 datetime 类型
    datetime1 = dt.datetime.now()
    show_var('datetime1', datetime1)

    # datetime类型 转换 timestamp类型
    timestamp4 = time.mktime(datetime1.timetuple())
    show_var('timestamp4', timestamp4)

    # str类型 转换 datetime类型
    time_str = 'Wed May 09 00:00:00 2018'
    datetime2 = dt.datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
    show_var('datetime2', datetime2)

    # str类型 转换 datetime类型
    time_str = '2022-07-23'
    date2 = dt.datetime.strptime('2022-07-23', "%Y-%m-%d").date()

    # 得到今天
    today = dt.date.today()
    show_var('today', today)

    # 得到日期间隔
    delta = dt.timedelta(days=1)
    yesterday = today - delta
    show_var('yesterday', yesterday)

    # 得到日期
    date1 = dt.date(2018, 7, 20)
    show_var('yesterday', yesterday)

    # 得到年月日
    month = date1.month
    year = date1.year
    day = date1.day

    show_var('month', month)
    show_var('year', year)
    show_var('day', day)

    # 得到上月
    today = dt.date.today()
    first = today.replace(day=1)
    date_tmp = first - dt.timedelta(days=1)
    show_var('date_tmp', date_tmp)

    date_str = date_tmp.strftime("%Y %m")
    show_var('date_str', date_str)

    # relativedelta工具
    from dateutil.relativedelta import relativedelta

    today = dt.date.today()
    next_month_day = today + relativedelta(months=5)
    show_var('next_month_day', next_month_day)
    print(dt.datetime.now())
