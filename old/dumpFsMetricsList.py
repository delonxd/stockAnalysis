from method.mainMethod import get_api_names, config_api_names, split_list
import pickle


if __name__ == '__main__':

    with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        codeList = pickle.load(pk_f)

    tables = ['bs', 'ps', 'cfs', 'm']

    files = [''.join(['Ns', value.capitalize(), 'Text.pkl']) for value in tables]

    subs = get_api_names(
        files=files,
        root='../basicData',
        regular=r'\n.* : (.*)',
    )

    apiAll = config_api_names(
        infix_list=subs,
        prefix='q',
        postfix='t',
    )

    metricsList = split_list(
        source=apiAll,
        length=100,
    )

    with open('../basicData/metricsList.pkl', 'wb') as pk_f:
        pickle.dump(metricsList, pk_f)
