import pickle
import json

if __name__ == '__main__':
    # with open('../basicData/metricsMvs.pkl', 'rb') as f:
    #     dict0 = pickle.load(f)
    #     # dict0 = json.loads(a)
    #     res = json.dumps(dict0, indent=4, ensure_ascii=False)
    #     print(res)
    #
    # with open("../comparisonTable/metrics_mvs.txt", "w", encoding='utf-8') as f:
    #     f.write(res)

    # with open('../comparisonTable/industries.txt', 'r', encoding='utf-8') as f:
    #     list0 = json.loads(f.read())['data']
    #     dict0 = dict()
    #     l1 = list()
    #     for tmp in list0:
    #         if tmp['level'] == 'three':
    #             dict0[tmp['stockCode']] = tmp['name']
    #             l1.append(tmp['stockCode'])
    #
    #     print(len(dict0))
    # #     res = json.dumps(dict0, indent=4, ensure_ascii=False)
    # #
    # # with open("../comparisonTable/industries_names_3.txt", "w", encoding='utf-8') as f:
    # #     f.write(res)
    #
    #     res = json.dumps(l1, indent=4, ensure_ascii=False)
    #
    #     with open("../comparisonTable/list_level_3_code.txt", "w", encoding='utf-8') as f:
    #         f.write(res)

    with open('../comparisonTable/stockCode_industries_3.txt', 'r', encoding='utf-8') as f:
        list0 = json.loads(f.read())['data']
        dict0 = dict()
        for tmp in list0:
            industries_code = tmp['stockCode']
            for sub in tmp['constituents']:
                dict0[sub['stockCode']] = industries_code

        print(len(dict0))

        res = json.dumps(dict0, indent=4, ensure_ascii=False)
        with open("../comparisonTable/dict_company2industries.txt", "w", encoding='utf-8') as f:
            f.write(res)