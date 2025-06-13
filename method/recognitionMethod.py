from method.fileMethod import load_json_txt
from method.fileMethod import load_pkl
# from method.logMethod import MainLog

import re
import json
import pandas as pd
import datetime as dt


class RecognitionStr:
    def __init__(self, src: str, df_all: pd.DataFrame, tag_flag=True, log=True):
        self.src = src
        self.tag_flag = tag_flag
        self.log = log

        symbol, values = self.config_symbol_values(src)
        symbol, values = self.replace_brace(symbol, values)
        self.symbol = symbol
        self.values = values

        self.df_all = df_all
        self.df_dict = dict()

        self.code_list = []
        self.sort_list = []

    def show(self):
        print(self.symbol)
        print(self.values)

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

    def calculate_set(self, symbol, val_dict) -> list:
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

    def get_code_list(self) -> list:
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
                self.values[0] = self.calculate_set(symbol, values)
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

                values2[start] = self.calculate_set(symbol1, values1)

                symbol = symbol2
                values = values2
                # print('c', symbol, values)

        self.code_list = self.values[0]
        return self.code_list

    def str_to_list(self, src) -> list:
        ret = []
        if isinstance(src, str):
            df = self.df_all

            src = src.strip('\n ')
            if src == 'all':
                ret = self.df_all.index.tolist()

            elif src == 'hold':
                if self.tag_flag is True:
                    tmp = load_json_txt("..\\basicData\\self_selected\\gui_hold.txt", self.log)
                    ret = list(zip(*tmp).__next__())
                else:
                    ret = self.df_all[self.df_all['gui_hold'].isin([True])].index.tolist()

            elif src == '持仓':
                tmp = load_json_txt("..\\basicData\\self_selected\\gui_hold.txt", self.log)
                new = []
                for val in tmp:
                    if val[2] != 0:
                        new.append(val)
                ret = list(zip(*new).__next__())

            elif src == 'old':
                ret = load_json_txt("..\\basicData\\tmp\\code_list_latest.txt", self.log)

            elif src == 'old_random':
                ret = load_json_txt("..\\basicData\\tmp\\code_list_random.txt", self.log)

            elif src == '持有行业':
                str0 = 'ids:3:医疗研发外包\n' \
                       '|ids:3:中药\n' \
                       '|ids:3:化学制剂\n' \
                       '|ids:3:农药\n' \
                       '|ids:3:快递\n' \
                       '|ids:3:线下药店\n'

                recognition = RecognitionStr(str0, self.df_all)
                ret = recognition.get_code_list()

            elif src[:6] == 'except':
                except_list = json.loads(src[6:])
                except_rec = load_json_txt("..\\basicData\\except_recognition.txt", self.log)

                str_list = []
                for index in except_list:
                    if index != except_rec[index][0]:
                        except_rec = self.refresh_except_recognition()
                    if except_rec[index][1] is False:
                        continue
                    if index == 0:
                        str_list.append('(except%s)' % list(range(1, len(except_rec))))
                    else:
                        str_list.append('(%s)' % except_rec[index][3])

                str0 = '|'.join(str_list)
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
                ret = self.industry2code(ids_name)

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

            elif src[:5] == 'ctrl:':
                condition = src[5:]
                s0 = df['controller_type'].astype(str)
                ret = s0[s0.str.contains(condition)].index.to_list()

            else:
                if self.tag_flag is True or 'gui_tags' not in df.columns:
                    path = "..\\basicData\\self_selected\\gui_tags.txt"
                    gui_tags = load_json_txt(path, log=self.log)
                    s0 = pd.Series(gui_tags)
                else:
                    s0 = df['gui_tags'].astype(str)

                txt = '#' + src
                return s0[s0.str.contains(txt)].index.to_list()

        elif isinstance(src, list):
            ret = src
        # elif isinstance(src, set):
        #     ret = list(src)
        else:
            raise KeyboardInterrupt('src类型错误')

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

        date_columns = [
            'found_date',
            'counter_date',
            'recent_date',
            'ipo_date',
            'report_date',
            'counter_last_date',
        ]

        value = split[1]
        if column in date_columns:
            if value[:1] == 'd':
                value = value[1:]
                try:
                    value = int(value)
                except ValueError:
                    return ret
                date_tmp = dt.date.today() - dt.timedelta(days=value)
                value = date_tmp.strftime("%Y-%m-%d")
            elif len(value) != 8:
                return ret
            else:
                value = '%s-%s-%s' % (value[:4], value[4:6], value[6:8])

            string = "df['%s'] %s '%s'" % (column, symbol, value)
        else:
            string = "df['%s'] %s %s" % (column, symbol, value)
        tmp = eval(string)

        df1 = df[tmp].copy()
        ret = df1.index.to_list()
        return ret

        # pattern = r'>=|<=|==|!=|<|>'
        # split = re.split(pattern, condition)
        # if len(split) == 2:
        #     symbol = re.search(pattern, condition).group(0)
        #     tmp1, tmp2 = split
        #     date_index = [
        #         'counter_date',
        #         'recent_date',
        #         'ipo_date',
        #         'report_date',
        #         'counter_last_date',
        #     ]
        #     if tmp1 in date_index:
        #         if len(tmp2) == 8:
        #             tmp2 = "'%s-%s-%s'" % (tmp2[:4], tmp2[4:6], tmp2[6:8])
        #
        #     string = "bool(self.data['%s'] %s %s)" % (tmp1, symbol, tmp2)
        #     try:
        #         flag = eval(string)
        #     finally:
        #         pass

    def market2code(self, market):
        ret = []
        code_all = self.df_all.index.tolist()

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

        elif market == 'B股':
            for code in code_all:
                if code[0] in ['2', '9']:
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

        elif market == '北交所':
            for code in code_all:
                if code[:2] in ['43', '82', '83', '87', '88']:
                    ret.append(code)

        return ret

    def industry2code(self, ids_name):
        df = self.df_all
        lst = ids_name.split(':')
        if len(lst) != 2:
            return list()

        column = 'level' + lst[0]
        if column not in df.columns:
            return list()

        return df[df[column] == lst[1]].index.to_list()

    @staticmethod
    def refresh_except_recognition():
        path = "..\\basicData\\except_recognition.txt"
        except_recognition = load_json_txt(path)
        ret = []
        for index, row in enumerate(except_recognition):
            row[0] = index
            ret.append(row)

        list0 = []
        for row in ret:
            tmp_txt = json.dumps(row, ensure_ascii=False)
            list0.append(tmp_txt)
        res = '[\n\t' + ',\n\t'.join(list0) + '\n]'

        with open(path, "w", encoding='utf-8') as f:
            f.write(res)
        return ret


def get_except_list(code, df_all, log=True):
    except_rec = load_json_txt("..\\basicData\\except_recognition.txt", log)
    ret = []
    for index, val in enumerate(except_rec):
        if index == 0:
            continue

        rec_str = val[3]
        code_list = RecognitionStr(rec_str, df_all, log=log).get_code_list()

        condition = val[5]
        if condition == '':
            if code in code_list:
                ret.append([val[2], val[4], True])
            else:
                ret.append([val[2], val[4], False])
        else:
            ret.append([val[2], val[4], condition])

    return ret


if __name__ == '__main__':
    # refresh_except_recognition()
    df0 = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl", log=False)
    # l0 = RecognitionStr('all-except[0]', df0)
    # code2 = l0.get_code_list()
    # print(len(code2))
    # l0.show()
    # print(get_except_list('600438', df0, log=False))
    # refresh_except_recognition()
    pass
