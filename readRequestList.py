from indexMethod import *

pathList = [
    'pkl/NsBsText.pkl',
    'pkl/NsPsText.pkl',
    'pkl/NsCfsText.pkl',
    'pkl/NsMText.pkl',
]
sheetNames = [
    '资产负债表',
    '利润表',
    '现金流量表',
    '财务指标',
]

stockCode = "600004"

path = 'SecurityData/FinancialSheet_%s.pkl' % stockCode
# path = 'SecurityData/allResNfFs.pkl'
with open(path, 'rb') as pk_f:
    resList = pickle.load(pk_f)

filepath = 'sheets/Fs_%s.xlsx' % stockCode

with pd.ExcelWriter(filepath) as writer:
    for index, path in enumerate(pathList):
        df, indexShow, headerShow = load_pkl(text_path=path, res_list=resList)
        df.to_excel(writer, sheet_name=sheetNames[index], index=indexShow, header=headerShow)

