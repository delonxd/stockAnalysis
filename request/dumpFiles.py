from method.mainMethod import get_api_names, config_api_names, split_list
import pickle
import json


def dump_fs_metrics_list():
    # with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
    #     codeList = pickle.load(pk_f)

    tables = ['bs', 'ps', 'cfs', 'm']

    files = [''.join(['Ns', value.capitalize(), 'Text.pkl']) for value in tables]

    subs = get_api_names(
        files=files,
        root='../basicData',
        regular=r'\n.* : (.*)',
    )

    api_all = config_api_names(
        infix_list=subs,
        prefix='q',
        postfix='t',
    )

    metrics_list = split_list(
        source=api_all,
        length=100,
    )

    res = json.dumps(metrics_list, indent=4, ensure_ascii=False)
    with open("../basicData/metrics/metrics_fs.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_mvs_metrics():
    files = ['priceText.pkl']
    metrics = get_api_names(
        files=files,
        root='../basicData',
        regular=r'\n.* :(.*)',
    )

    print(metrics)

    res = json.dumps(metrics, indent=4, ensure_ascii=False)
    with open("../basicData/metrics/metrics_mvs.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_nf_codes():
    with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        code_list = pickle.load(pk_f)

    res = json.dumps(code_list, indent=4, ensure_ascii=False)
    print(res)

    with open("../basicData/list_nf_codes.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_list_code_names():
    with open('../basicData/code_name.pkl', 'rb') as pk_f:
        code_name = pickle.load(pk_f)

    res = json.dumps(code_name, indent=4, ensure_ascii=False)
    print(res)

    with open("../basicData/dict_code2names.txt", "w", encoding='utf-8') as f:
        f.write(res)


if __name__ == '__main__':
    # dump_fs_metrics_list()
    # dump_nf_codes()
    dump_list_code_names()
