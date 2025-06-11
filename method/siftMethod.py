from method.recognitionMethod import RecognitionStr
from method.fileMethod import load_json_txt
from method.fileMethod import write_json_txt
from method.logMethod import MainLog
from method.profileMethod import get_code_profile_df

import datetime as dt
import pandas as pd


class SiftCode:
    def __init__(
            self,
            source='',
            sort=None,
            ascending=None,
            sort_ids=False,
            random=False,
            interval=100,
            df_all: pd.DataFrame | None = None,
    ):
        if df_all is None:
            self.df_all = get_code_profile_df()
        else:
            self.df_all = df_all

        self._code_list = RecognitionStr(source, self.df_all).get_code_list()

        self.sort_codes(sort, ascending, sort_ids)

        if random is True:
            self.random(interval)

    @property
    def code_list(self) -> list:
        return self._code_list

    def sort_codes(self, sort, ascending, ids_sort=False) -> list:
        code_list = self._code_list
        df = self.df_all.reindex(index=code_list).copy()

        if sort is None:
            return code_list
        elif not isinstance(sort, list):
            sort = [sort]

        if ascending is None:
            ascending = []
        elif not isinstance(ascending, list):
            ascending = [ascending]

        columns = df.columns

        df_sort = []
        df_ascending = []

        if ids_sort is True:
            df_sort.append('level3')
            df_ascending.append(True)

        for index, kw in enumerate(sort):
            if kw in columns:
                df_sort.append(kw)
                if index >= len(ascending):
                    condition = True
                else:
                    condition = ascending[index]
                df_ascending.append(condition)

        df = df.sort_values(by=df_sort, ascending=df_ascending)
        self._code_list = df.index.tolist()
        return self._code_list

    def random(self, interval) -> list:
        code_list = self._code_list
        weight_dict = SiftCode.get_weight_dict(code_list)
        random_list = SiftCode.generate_random_list(code_list, weight_dict)

        ret = list()
        pick_list = list()
        counter = 0
        group = 0
        while True:

            code = random_list.pop(0)
            pick_list.append(code)
            counter += 1

            length = len(random_list)
            if counter == interval or length == 0:
                group += 1
                sub_list = list()
                for key in code_list:
                    if key in pick_list:
                        sub_list.append(key)
                ret.extend(sub_list)

                if length == 0:
                    break
                pick_list = list()
                counter = 0

        MainLog.add_log('pick --> [%s] * %s, [%s]' % (interval, group, counter))

        write_json_txt("..\\basicData\\tmp\\code_list_random.txt", ret)
        MainLog.add_split('#')

        self._code_list = ret
        return self._code_list

    @classmethod
    def get_weight_dict(cls, set_all):
        path = "..\\basicData\\dailyUpdate\\latest\\a003_report_date_dict.txt"
        report_date_dict = load_json_txt(path, log=False)

        base_rate = 10000000
        weight_dict = dict.fromkeys(set_all, base_rate * 3000)

        # date1 = dt.date.today()
        path = "..\\basicData\\dailyUpdate\\latest\\a000_log_data.txt"
        date_txt = load_json_txt(path, log=False)['update_date']
        date1 = dt.datetime.strptime(date_txt, '%Y-%m-%d').date()

        path = "..\\basicData\\self_selected\\gui_counter.txt"
        gui_counter = load_json_txt(path, log=False)

        counter = 0
        counter1 = 0
        counter_new = len(weight_dict)
        for key, value in gui_counter.items():
            if key not in set_all:
                continue

            report_date = report_date_dict.get(key)
            if report_date is None or report_date == 'Invalid da':
                report_date = ''

            flag = True if report_date > value[1] else False

            date2 = dt.datetime.strptime(value[1], '%Y-%m-%d').date()
            margin = (date1 - date2).days

            if flag is True:
                weight = margin ** 2 * base_rate
                # MainLog.add_log('%s %s %s margin == 1' % (key, report_date, value[1]))
                counter1 += 1
            elif margin > 60:
                weight = margin ** 2 * 100
                # MainLog.add_log('%s %s margin > 60' % (key, value[1]))
                counter += 1
            else:
                weight = margin ** 2

            weight_dict[key] = weight
            counter_new -= 1

        weight_counter = dict()
        for weight in weight_dict.values():
            if weight in weight_counter:
                weight_counter[weight] += 1
            else:
                weight_counter[weight] = 1

        MainLog.add_split('-')

        weight_list = list(weight_counter.keys())
        weight_list.sort()
        for weight in weight_list:
            if weight % base_rate == 0:
                margin = (weight / base_rate) ** 0.5
            else:
                margin = weight ** 0.5

                if margin > 60:
                    margin = margin / 10

            date2 = date1 - dt.timedelta(days=margin)
            date_str = dt.date.strftime(date2, '%Y-%m-%d')

            weight_str = '%s%18s%8s' % (date_str, weight, weight_counter[weight])
            MainLog.add_log(weight_str)

        MainLog.add_log('      total:  %10s' % len(set_all))
        MainLog.add_log('        new:  %10s' % counter_new)
        MainLog.add_log('margin < -1:  %10s' % counter1)
        MainLog.add_log('margin > 60:  %10s' % counter)
        MainLog.add_split('-')

        return weight_dict

    @classmethod
    def generate_random_list(cls, src, weight_dict: dict):
        length = len(src)
        set_all = set(src)

        ret = []
        for _ in range(length):
            code = cls.random_by_weight(set_all, weight_dict)
            set_all -= {code}
            ret.append(code)
        return ret

    @classmethod
    def random_by_weight(cls, src, weight_dict: dict):
        import random

        total = 0
        for code in src:
            total += weight_dict.get(code)
        ra = random.uniform(0, total)

        current = 0
        for code in src:
            current += weight_dict.get(code)
            if ra <= current:
                return code


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # sift_codes(source='kk{(m2{zz{白名单}-xx{hold}}-m3{自选})-()|()}')
    # sift_codes(source='backup:20230816:{hold}')
    # print(SiftCode(source='ids:1:综合企业').code_list)
    print(SiftCode(source='ctrl:国有').code_list)
