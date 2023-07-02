import json
import pickle
import pandas as pd

def test_json():

    # path = '../gui/style_combined_default0.pkl'
    # path = '..\\gui\\styles\\style_20211111135706.pkl'
    # with open(path, 'rb') as pk_f:
    #     df = pickle.load(pk_f)
    #
    # tmp_str = ''
    # for index, row in df.iterrows():
    #
    #     # print(index)
    #     # print(row.values)
    #
    #     row_str = ' | '.join([row['txt_CN'], row['index_name']])
    #     tmp_str = '\n'.join([tmp_str, row_str])
    #
    # # df = pd.DataFrame()
    # # print(df)
    # # tmp = df.to_json(orient="columns", force_ascii=False)
    # # tmp = df.to_json(orient="split", force_ascii=False, indent=4)
    # str1 = df.to_json(orient="index", force_ascii=False)
    #
    # dict0 = json.loads(str1)
    # # res = json.dumps(tmp)
    # print(dict0)
    #
    # res = json.dumps(dict0, indent=4, ensure_ascii=False)
    # with open("../test/style_test.txt", "w", encoding="utf-8") as f:
    #     f.write(res)
    # pass

    a = 'time>4123'
    ret = json.loads(a)
    print(ret)


if __name__ == '__main__':
    test_json()
