from method.mainMethod import get_api_names, config_api_names, split_list
import pickle


if __name__ == '__main__':
    files = ['priceText.pkl']
    metrics = get_api_names(
        files=files,
        root='../basicData',
        regular=r'\n.* :(.*)',
    )

    print(metrics)

    with open('../basicData/metricsMvs.pkl', 'wb') as pk_f:
        pickle.dump(metrics, pk_f)
