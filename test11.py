import pickle


with open('SecurityData/nfCodeList.pkl', 'rb') as pk_f:
    codeList = pickle.load(pk_f)


tmpDict = dict()

# stockCode = "000002"
for stockCode in codeList:

    path = 'SecurityData/FinancialSheet_%s.pkl' % stockCode
    with open(path, 'rb') as pk_f:
        reqList = pickle.load(pk_f)

    print(stockCode)
    tmpDict[stockCode] = reqList

with open('SecurityData/allStockFs.pkl', 'wb') as pk_f:
    pickle.dump(tmpDict, pk_f)
