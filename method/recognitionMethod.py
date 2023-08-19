from method.fileMethod import *
import re
import pandas as pd


class RecognitionStr:
    def __init__(self, src: str, df_all, tag_flag=True):
        self.src = src
        self.tag_flag = tag_flag

        symbol, values = self.config_symbol_values(src)
        symbol, values = self.replace_brace(symbol, values)
        self.symbol = symbol
        self.values = values

        self.df_all = df_all
        self.df_dict = dict()
        self.code_all = None
        self.sw_2021_name_dict = None
        self.sw_2021_dict = None

        self.code_list = []
        self.sort_list = []

    @staticmethod
    def config_symbol_values(src):
        symbol = ''
        values = dict()

        counter = 0
        while src != '':
            match = re.search(r'[{}()&|-]', src)

            if match is None:
                values[counter] = src
                break

            pos = match.start()

            if pos > 0:
                values[counter] = src[:pos]
            src = src[pos+1:]

            # print(src)
            symbol = ''.join([symbol, match.group()])
            counter += 1
        return symbol, values

    @staticmethod
    def replace_brace(symbol, values):

        while True:
            m1 = re.search(r'}', symbol)

            if m1 is None:
                if re.search(r'{', symbol) is not None:
                    raise KeyboardInterrupt('大括号数量不匹配')
                break
            else:
                end = m1.end()
                m2 = re.search(r'.*{', symbol[:end])
                if m2 is None:
                    raise KeyboardInterrupt('大括号数量不匹配')
                start = m2.end() - 1

                if start in values.keys():
                    pre = values.pop(start)

                    for key in values.keys():
                        if start < key < end:
                            values[key] = ''.join([pre, values[key]])

                symbol1 = symbol[:start]
                symbol2 = symbol[start + 1: end - 1]
                symbol3 = symbol[end:]
                symbol = ''.join([symbol1, '(', symbol2, ')', symbol3])

        return symbol, values

    def set_calculate(self, symbol, val_dict):
        if symbol == '':
            if len(val_dict) == 0:
                return []
            else:
                return self.str_to_list(val_dict[0])
        values = []
        for index in range(len(symbol) + 1):
            if index not in val_dict.keys():
                raise KeyboardInterrupt('集合运算符错误')
            values.append(val_dict.pop(index))
        if len(val_dict) > 0:
            raise KeyboardInterrupt('集合运算符错误')

        while symbol != '':

            if '&' in symbol:
                reg = r'&'
            elif '|' in symbol:
                reg = r'\|'
            elif '-' in symbol:
                reg = r'-'
            else:
                raise KeyboardInterrupt('集合运算符错误')

            pos = re.search(reg, symbol).start()
            set1 = set(self.str_to_list(values[pos]))
            set2 = set(self.str_to_list(values[pos+1]))

            if reg == r'&':
                new = set1 & set2
            elif reg == r'\|':
                new = set1 | set2
            else:
                new = set1 - set2

            values2 = []
            for index in range(len(symbol)):
                if index < pos:
                    values2.append(values[index])
                elif index > pos:
                    values2.append(values[index+1])
                else:
                    values2.append(list(new))

            symbol = ''.join([symbol[:pos], symbol[pos+1:]])
            values = values2

        return values[0]

    def get_code_list(self):
        symbol = self.symbol
        values = self.values
        # print(symbol, values)

        while True:
            m1 = re.search(r'\)', symbol)
            if m1 is None:
                if re.search(r'\(', symbol) is not None:
                    raise KeyboardInterrupt('括号数量错误')
                self.symbol = ''
                self.values = dict()
                self.values[0] = self.set_calculate(symbol, values)
                break
            else:
                end = m1.end()
                m2 = re.search(r'.*\(', symbol[:end])
                if m2 is None:
                    raise KeyboardInterrupt('括号数量错误')
                start = m2.end() - 1

                symbol1 = symbol[start + 1: end - 1]
                symbol2 = ''.join([symbol[:start], symbol[end:]])
                values1 = dict()
                values2 = dict()

                for key, value in values.items():
                    if key <= start:
                        values2[key] = value
                    elif key >= end:
                        values2[key + start - end] = value
                    else:
                        values1[key - start - 1] = value

                # print('a', symbol1, values1)
                # print('b', symbol2, values2)

                values2[start] = self.set_calculate(symbol1, values1)

                symbol = symbol2
                values = values2
                # print('c', symbol, values)

        self.code_list = self.values[0]
        return self.code_list

    def get_code_all(self):
        if self.tag_flag is True:
            self.code_all = load_json_txt("..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt")
        else:
            self.code_all = self.df_all.index.tolist()
        return self.code_all

    def str_to_list(self, src):
        ret = []
        if isinstance(src, str):
            src = src.strip('\n ')
            if src == 'all':
                ret = self.get_code_all()

            elif src == 'hold':
                if self.tag_flag is True:
                    tmp = load_json_txt("..\\basicData\\self_selected\\gui_hold.txt")
                    ret = list(zip(*tmp).__next__())
                else:
                    ret = self.df_all[self.df_all['gui_hold'].isin([True])].index.tolist()

            elif src == 'old':
                ret = load_json_txt("..\\basicData\\tmp\\code_list_latest.txt")

            elif src == 'old_random':
                ret = load_json_txt("..\\basicData\\tmp\\code_list_random.txt")

            elif src == '持有行业':
                str0 = 'ids:3:医疗研发外包\n' \
                       '|ids:3:中药\n' \
                       '|ids:3:化学制剂\n' \
                       '|ids:3:农药\n' \
                       '|ids:3:快递\n' \
                       '|ids:3:线下药店\n'

                recognition = RecognitionStr(str0, self.df_all)
                ret = recognition.get_code_list()

            # elif src[:4] == 'mark':
            #     # mark = int(src.split('-')[1])
            #     mark = src.split('-')[1]
            #     mark_dict = load_json_txt("..\\basicData\\self_selected\\gui_mark.txt")
            #
            #     if mark == '0':
            #         ret = list(mark_dict.keys())
            #     else:
            #         ret = []
            #         for code, value in mark_dict.items():
            #             if value == mark:
            #                 ret.append(code)

            elif src == 'plate50':
                path = "..\\basicData\\self_selected\\板块50.txt"
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                    ret = re.findall(r'([0-9]{6})', txt)
                    ret.reverse()

            elif src[:5] == 'time>':
                with open("..\\basicData\\self_selected\\gui_timestamp.txt", "r", encoding="utf-8",
                          errors="ignore") as f:
                    gui_timestamp = json.loads(f.read())

                timestamp = src[5:]
                for key, value in gui_timestamp.items():
                    if value > timestamp:
                        ret.append(key)
                        # print('sift:', key, value)

            elif src[:4] == 'mkt:':
                market = src[4:]
                ret = self.market2code(market)

            elif src[:4] == 'ids:':
                ids_name = src[4:]
                ret = self.industry_name2code(ids_name)

            elif src[:4] == 'cnd:':
                condition = src[4:]
                ret = self.condition2code(condition)

            elif src[:7] == 'backup:':
                str1 = src[7:]
                m1 = re.search(r':', str1)
                date = str1[:m1.start()]
                str2 = str1[m1.end():]
                if date not in self.df_dict.keys():
                    path = "..\\basicData\\backups\\df_all\\df_all_%s.pkl" % date
                    tmp_df = load_pkl(path)
                    self.df_dict[date] = tmp_df
                tmp_df = self.df_dict[date]

                recognition = RecognitionStr(str2, tmp_df, tag_flag=False)
                ret = recognition.get_code_list()

            else:
                if self.tag_flag is True:
                    ret = code_list_from_tags(src)
                else:
                    ret = self.code_list_from_df(src)

        elif isinstance(src, list):
            ret = src
        # elif isinstance(src, set):
        #     ret = list(src)
        else:
            raise KeyboardInterrupt('src类型错误')

        return ret

    def code_list_from_df(self, column):
        df = self.df_all
        ret = []
        if column in df.columns:
            ret = df[df[column].isin([True])].index.tolist()
        return ret

    def show(self):
        print(self.symbol)
        print(self.values)

    def get_sort_list(self, sort, ascending, ids_sort=False):

        self.sort_list = self.code_list

        if sort is None:
            return self.sort_list

        if not isinstance(sort, list):
            sort = [sort]

        if ascending is None:
            ascending = []
        elif not isinstance(ascending, list):
            ascending = [ascending]

        if self.df_all is not None:
            columns = self.df_all.columns

            df_sort = []
            df_ascending = []
            for index, kw in enumerate(sort):
                if kw in columns:
                    df_sort.append(kw)
                    if index >= len(ascending):
                        condition = True
                    else:
                        condition = ascending[index]
                    df_ascending.append(condition)

            df = self.df_all.loc[self.code_list, :].copy()
            if len(df_sort) > 0:
                df = df.sort_values(by=df_sort, ascending=df_ascending)

            self.sort_list = df.index.tolist()

        if ids_sort is True:
            if self.df_all is not None:
                s0 = self.df_all.loc[self.sort_list, 'level3'].copy()
                s1 = s0.drop_duplicates()
                new = pd.Series()
                for level3 in s1.values:
                    s2 = s0[s0 == level3]
                    new = new.append(s2)
                s2 = s0[pd.isna(s0)]
                new = new.append(s2)

                new_list = new.keys().tolist()

                if len(new_list) == len(self.sort_list):
                    self.sort_list = new_list
                else:
                    print('len(new_list) != len(self.sort_list)')
                    self.sort_list = []

        return self.sort_list

    def random(self, interval):

        weight_dict = get_weight_dict(self.code_list)
        random_list = generate_random_list(self.code_list, weight_dict)

        ret = []
        pick_list = []
        counter = 0
        group = 0
        while True:

            code = random_list.pop(0)
            pick_list.append(code)
            counter += 1

            length = len(random_list)
            if counter == interval or length == 0:
                group += 1
                sub_list = []
                for key in self.sort_list:
                    if key in pick_list:
                        sub_list.append(key)
                ret.extend(sub_list)

                if length == 0:
                    break
                pick_list = []
                counter = 0

        MainLog.add_log('pick --> [%s] * %s, [%s]' % (interval, group, counter))

        write_json_txt("..\\basicData\\tmp\\code_list_random.txt", ret)
        MainLog.add_split('#')

        return ret

    def condition2code(self, condition):
        ret = []
        if self.df_all is None:
            return ret

        if '>=' in condition:
            symbol = '>='
        elif '<=' in condition:
            symbol = '<='
        elif '==' in condition:
            symbol = '=='
        elif '!=' in condition:
            symbol = '!='
        elif '<' in condition:
            symbol = '<'
        elif '>' in condition:
            symbol = '>'
        else:
            return ret

        split = condition.split(symbol)
        if len(split) != 2:
            return ret

        column = split[0]
        df = self.df_all.copy()

        if column not in df.columns:
            return ret

        string = "df['%s'] %s %s" % (column, symbol, split[1])
        tmp = eval(string)

        df1 = df[tmp].copy()
        ret = df1['code'].to_list()
        return ret

    def market2code(self, market):
        ret = []
        if self.code_all is None:
            self.get_code_all()
        code_all = self.code_all

        if market == 'all':
            ret = code_all

        elif market == 'main':
            for code in code_all:
                if code[0] in ['0', '3', '6'] and code[:3] != '688':
                    ret.append(code)

        elif market == '上证A股':
            for code in code_all:
                if code[0] == '6' and code[:3] != '688':
                    ret.append(code)

        elif market == '深证A股':
            for code in code_all:
                if code[0] == '0':
                    ret.append(code)

        elif market == '上证B股':
            for code in code_all:
                if code[0] == '9':
                    ret.append(code)

        elif market == '深证B股':
            for code in code_all:
                if code[0] == '2':
                    ret.append(code)

        elif market == '创业板':
            for code in code_all:
                if code[0] == '3':
                    ret.append(code)

        elif market == '科创板':
            for code in code_all:
                if code[:3] == '688':
                    ret.append(code)

        elif market == '新三板':
            for code in code_all:
                if code[0] in ['4', '8']:
                    ret.append(code)
        return ret

    def industry_name2code(self, ids_name):
        if self.sw_2021_name_dict is None:
            self.sw_2021_name_dict = load_json_txt('..\\basicData\\industry\\sw_2021_name_dict.txt')

        if self.sw_2021_dict is None:
            self.sw_2021_dict = load_json_txt('..\\basicData\\industry\\sw_2021_dict.txt')

        ids_codes = []
        index = -1
        for key, name in self.sw_2021_name_dict.items():
            if key[-4:] == '0000':
                flag = 1
            elif key[-2:] == '00':
                flag = 2
            else:
                flag = 3

            tmp_name = '%s:%s' % (flag, name)

            if tmp_name == ids_name:
                ids_codes.append(key)
                index = flag * 2

        ret = []
        for key, value in self.sw_2021_dict.items():
            if value is None:
                continue

            for ids_code in ids_codes:
                if value[:index] == ids_code[:index]:
                    ret.append(key)
        return ret


def get_weight_dict(set_all):
    path = "..\\basicData\\dailyUpdate\\latest\\a003_report_date_dict.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        report_date_dict = json.loads(f.read())

    base_rate = 10000000
    weight_dict = dict.fromkeys(set_all, base_rate * 3000)

    # date1 = dt.date.today()
    path = "..\\basicData\\dailyUpdate\\latest\\a000_log_data.txt"
    date_txt = load_json_txt(path)['update_date']
    date1 = dt.datetime.strptime(date_txt, '%Y-%m-%d').date()

    with open("..\\basicData\\self_selected\\gui_counter.txt", "r", encoding="utf-8", errors="ignore") as f:
        gui_counter = json.loads(f.read())

    counter = 0
    counter1 = 0
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
    MainLog.add_log('margin > 60:  %10s' % counter)
    MainLog.add_log('margin < -1:  %10s' % counter1)
    MainLog.add_split('-')

    return weight_dict


def generate_random_list(src, weight_dict: dict):
    length = len(src)
    set_all = set(src)

    ret = []
    for _ in range(length):
        code = random_by_weight(set_all, weight_dict)
        set_all -= {code}
        ret.append(code)
    return ret


def random_by_weight(src, weight_dict: dict):
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


def industry_name2code(ids_names):
    name_dict = load_json_txt('..\\basicData\\industry\\sw_2021_name_dict.txt')

    ids_codes = []

    for ids_code, name in name_dict.items():
        if ids_code[-4:] == '0000':
            ids_name = '1:' + name
        elif ids_code[-2:] == '00':
            ids_name = '2:' + name
        else:
            ids_name = '3:' + name

        if ids_name in ids_names:
            ids_codes.append(ids_code)

    sw_2021_dict = load_json_txt('..\\basicData\\industry\\sw_2021_dict.txt')

    ret = []
    for code, ids_code1 in sw_2021_dict.items():
        if ids_code1 is None:
            continue

        for ids_code2 in ids_codes:
            if ids_code2[-4:] == '0000':
                index = 2
            elif ids_code2[-2:] == '00':
                index = 4
            else:
                index = 6

            if ids_code1[:index] == ids_code2[:index]:
                ret.append(code)
    return ret


if __name__ == '__main__':

    # l0 = RecognitionStr('hold')
    # code2 = l0.get_code_list()
    # print(code2)
    # l0.show()
    pass
