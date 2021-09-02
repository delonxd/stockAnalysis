import pandas as pd


def write2excel(
        root,
        file_name,
        sheet_name,
        data_frame,
        header=None,
        index=False):

    path = '%s/%s' % (root, file_name)

    with pd.ExcelWriter(path) as writer:
        data_frame.to_excel(writer, sheet_name=sheet_name, index=index, header=header)