import json
import pickle


def test_json():

    path = '../gui/style_combined_default0.pkl'
    with open(path, 'rb') as pk_f:
        df = pickle.load(pk_f)

    tmp_str = ''
    for index, row in df.iterrows():

        print(index)
        print(row.values)

        row_str = ' | '.join([row['txt_CN'], row['index_name']])
        tmp_str = '\n'.join([tmp_str, row_str])

    # print(df)
    # tmp = df.to_json(orient="columns", force_ascii=False)
    tmp = df.to_json(orient="split", force_ascii=False)

    # res = json.dumps(tmp)

    with open("../test/style_test.txt", "w", encoding="utf-8") as f:
        f.write(tmp)
    pass


if __name__ == '__main__':
    test_json()
