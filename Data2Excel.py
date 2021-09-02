import pandas as pd

class Data2Excel:
    def __init__(self, sheet_names):
        self.sheet_names = sheet_names
        self.data_dict = {}
        self.dataframes = {}
        for name in sheet_names:
            self.data_dict[name] = []

    def add_row(self):
        for value in self.data_dict.values():
            value.append([])

    def add_sheet_name(self, sheet_name):
        self.data_dict[sheet_name] = []

    def add_dataframes(self, sheet_name, dataframe):
        self.dataframes[sheet_name] = dataframe

    def add_data(self, sheet_name, data1):
        if sheet_name in self.data_dict.keys():
            self.data_dict[sheet_name][-1].append(data1)
        else:
            self.data_dict[sheet_name] = [[]]
            self.data_dict[sheet_name][-1].append(data1)

    # def create_dataframes(self):
    #     for name, value in self.data_dict.items():
    #         self.dataframes[name] = pd.DataFrame(value)

    def write2excel(self, sheet_names, header, writer1):
        for key_name in sheet_names:
            # df_output = pd.DataFrame(self.data_dict[key_name], columns=header)
            df_output = pd.DataFrame(self.data_dict[key_name])
            columns = len(df_output.columns)

            header_t = header[:columns]
            df_output.to_excel(writer1, sheet_name=key_name, index=False, header=header_t)


class SheetDataGroup:
    def __init__(self, sheet_names):
        self.sheet_names = sheet_names
        self.data_dict = {}
        self.dataframes = {}
        for name in sheet_names:
            self.data_dict[name] = SheetData(name=name)


    def add_new_row(self):
        for ele in self.data_dict.values():
            ele.add_new_row()

    def add_new_sheet(self, sheet_name):
        self.sheet_names.append(sheet_name)
        self.data_dict[sheet_name] = SheetData(name=sheet_name)

    def add_dataframes(self, sheet_name, dataframe):
        self.dataframes[sheet_name] = dataframe

    def add_data(self, sheet_name, data1):
        if not sheet_name in self.data_dict.keys():
            self.add_new_sheet(sheet_name=sheet_name)
            self.data_dict[sheet_name].add_new_row()
        self.data_dict[sheet_name].add_data(data1)

    def write2excel(self, sheet_names, writer):
        for name in sheet_names:
            self.data_dict[name].write2excel(writer)

    def config_header(self):
        for ele in self.data_dict.values():
            ele.config_header(header=None)

    def __getitem__(self, key):
        return self.data_dict[key]

    def __setitem__(self, key, value):
        self.data_dict[key] = value


class SheetData:
    def __init__(self, name):
        self.name = name
        self.data_list = []
        self.header = []

    def add_new_row(self):
        self.data_list.append([])

    def add_data(self, data):
        self.data_list[-1].append(data)

    def config_header(self, header):
        self.header = []
        len_colunm = 0
        if header is None:
            for data in self.data_list:
                len_colunm = max(len_colunm, len(data))
            self.header = list(range(len_colunm))
        else:
            self.header = header

    def write2excel(self, writer):
        df_output = pd.DataFrame(self.data_list)
        # df_temp = pd.DataFrame(self.data_list)
        # df_output = pd.DataFrame(df_temp.values.T)
        df_output.to_excel(writer, sheet_name=self.name, index=False, header=self.header)
        # df_output.to_excel(writer, sheet_name=self.name, index=False, header=None)

    def __getitem__(self, key):
        return self.data_list[key]

    def __setitem__(self, key, value):
        self.data_list[key] = value

