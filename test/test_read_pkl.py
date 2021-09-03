from method.mainMethod import *

if __name__ == '__main__':
    res = read_pkl(
        root='../basicData',
        file_name='NsBsText.pkl'
    )
    print(res)
    print(type(res))
