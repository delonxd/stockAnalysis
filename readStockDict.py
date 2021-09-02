import pickle
import json


class Stock:
    def __init__(self):
        self.stockCode = None
        self.areaCode = None
        self.market = None
        self.ipoDate = None
        self.name = None
        self.fsType = None


if __name__ == '__main__':
    path = 'SecurityData/BasicData.pkl'

    with open(path, 'rb') as pk_f:
        info = pickle.load(pk_f)

    info_dict = json.loads(info)
    data = info_dict['data']

    codeList = list()

    stockDict = dict()
    for index in range(len(data)):
        stockData = data[index]

        stock = Stock()
        stock.stockCode = stockData.get('stockCode')
        stock.market = stockData.get('market')
        stock.ipoDate = stockData.get('ipoDate')
        stock.areaCode = stockData.get('areaCode')
        stock.name = stockData.get('name')
        stock.fsType = stockData.get('fsType')

        if stock.fsType == 'non_financial' and stock.market == 'a':
            stockDict.update({stock.stockCode: stock})
            codeList.append(stock.stockCode)
            print(stock.market, stock.fsType)

    print(len(stockDict))

    # with open('SecurityData/stockDict.pkl', 'wb') as pk_f:
    #     pickle.dump(stockDict, pk_f)

    with open('SecurityData/nfCodeList.pkl', 'wb') as pk_f:
        pickle.dump(codeList, pk_f)
