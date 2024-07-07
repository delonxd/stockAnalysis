# def update_counter_old(self, code):
#     df = self.data_pix.df
#
#     last_date = ''
#     last_real_pe = np.inf
#     number = 0
#
#     if df.columns.size > 0:
#         date = self.date_ini
#     else:
#         date = ''
#
#     real_pe = np.inf
#     # tmp_date = ''
#     if 's_034_real_pe' in df.columns:
#         s0 = self.data_pix.df['s_034_real_pe'].copy().dropna()
#         if s0.size > 0:
#             # tmp_date = max(s0.index[-1], tmp_date)
#             real_pe = s0[-1]
#
#     # if 'dt_fs' in df.columns:
#     #     s0 = self.data_pix.df['dt_fs'].copy().dropna()
#     #     if s0.size > 0:
#     #         tmp_date = max(s0.index[-1], tmp_date)
#     #
#     # if tmp_date != '' and tmp_date != 'Invalid da':
#     #     date = tmp_date
#
#     self.max_increase_30 = np.inf
#     self.listing_date = None
#     self.market_value = np.nan
#     self.yesterday_rise = np.nan
#     if 's_028_market_value' in df.columns:
#         s0 = self.data_pix.df['s_028_market_value'].copy().dropna()
#         if s0.size > 0:
#             recent = s0[-1]
#             self.market_value = recent / 1e8
#
#             size0 = min(s0.size, 90)
#             minimum = min(s0[-size0:])
#             self.max_increase_30 = recent / minimum - 1
#             self.listing_date = s0.index[0]
#         if s0.size > 1:
#             self.yesterday_rise = s0[-1] / s0[-2] - 1
#
#     self.liquidation_asset = np.nan
#     if 's_026_liquidation_asset' in df.columns:
#         s0 = self.data_pix.df['s_026_liquidation_asset'].copy().dropna()
#         if s0.size > 0:
#             self.liquidation_asset = s0[-1] / 1e8
#
#     self.real_cost = np.nan
#     if 's_025_real_cost' in df.columns:
#         s0 = self.data_pix.df['s_025_real_cost'].copy().dropna()
#         if s0.size > 0:
#             self.real_cost = s0[-1] / 1e8
#
#     self.turnover = 0
#     if 's_043_turnover_volume_ttm' in df.columns:
#         s0 = self.data_pix.df['s_043_turnover_volume_ttm'].copy().dropna()
#         if s0.size > 0:
#             self.turnover = s0[-1]
#
#     self.equity = np.nan
#     if 's_002_equity' in df.columns:
#         s0 = self.data_pix.df['s_002_equity'].copy().dropna()
#         if s0.size > 0:
#             self.equity = s0[-1] / 1e8
#
#     self.profit_salary_min = np.nan
#     self.predict_delta = 0
#     tmp_date = np.nan
#
#     if 's_063_profit_salary2' in df.columns:
#         s0 = self.data_pix.df['s_063_profit_salary2'].copy().dropna()
#         if s0.size > 0:
#             self.profit_salary_min = s0[-1]
#             tmp_date = s0.index[-1]
#
#     if not pd.isna(tmp_date):
#         date1 = dt.datetime.strptime(tmp_date, "%Y-%m-%d").date()
#         date2 = dt.date.today()
#         self.predict_delta = (date2 - date1).days
#
#     self.dividend_return = 0
#     if 's_069_dividend_rate' in df.columns:
#         s0 = self.data_pix.df['s_069_dividend_rate'].copy().dropna()
#         if s0.size > 0:
#             self.dividend_return = s0[-1] * 100
#
#     path = "../basicData/self_selected/gui_counter.txt"
#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         res_dict = json.loads(f.read())
#         data = res_dict.get(code)
#
#     if isinstance(data, list):
#         last_date = data[1]
#         number = data[2]
#         last_real_pe = data[3]
#     elif data is not None:
#         number = data
#
#     path = "..\\basicData\\dailyUpdate\\latest\\a003_report_date_dict.txt"
#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         report_date = json.loads(f.read()).get(code)
#
#     color = Qt.GlobalColor.red
#
#     if report_date is not None:
#         if data is None:
#             color = Qt.GlobalColor.white
#         elif data[1] < report_date:
#             color = Qt.GlobalColor.white
#         elif self.date_ini == data[1]:
#             if data[0] < report_date:
#                 color = Qt.GlobalColor.white
#
#     p = QPalette()
#     p.setColor(QPalette.WindowText, color)
#     self.head_label1.setPalette(p)
#
#     if date > last_date:
#         number += 1
#         delta = (1/real_pe - 1/last_real_pe) * abs(last_real_pe)
#         self.counter_info = [last_date, date, number, real_pe, delta]
#         res_dict[code] = self.counter_info
#         res = json.dumps(res_dict, indent=4, ensure_ascii=False)
#         path = "../basicData/self_selected/gui_counter.txt"
#         with open(path, "w", encoding='utf-8') as f:
#             f.write(res)
#     else:
#         self.counter_info = res_dict.get(code)
#
#     path = "../basicData/self_selected/gui_timestamp.txt"
#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         timestamps = json.loads(f.read())
#
#     timestamps[code] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
#
#     res = json.dumps(timestamps, indent=4, ensure_ascii=False)
#     with open(path, "w", encoding='utf-8') as f:
#         f.write(res)
#
# def show_stock_name_old(self):
#     row = self.codes_df.df.iloc[self.code_index]
#     len_df = self.codes_df.df.shape[0]
#
#     txt1 = '%s: %s(%s/%s)' % (row['code'], row['name'], self.code_index, len_df)
#     txt2 = '行业: %s-%s-%s' % (row['level1'], row['level2'], row['level3'])
#
#     code = row['code']
#     list0 = []
#     list1 = []
#
#     path = "..\\basicData\\self_selected\\gui_tags.txt"
#
#     tags_dict = load_json_txt(path, log=False)
#     txt = tags_dict.get(code)
#     txt = '' if txt is None else txt
#     tags_list = txt.split('#')
#     tags_list.pop(tags_list.index(''))
#
#     tmp = {
#         'Src': 'Src',
#         'Toc': 'ToC',
#         'Mid': 'Mid',
#         '排除': '排',
#         '自选': '自选',
#         '白名单': '白',
#         '黑名单': '黑',
#         '灰名单': '灰',
#         '周期': '周期',
#         '疫情': '疫',
#         '忽略': '忽略',
#         '国有': '国',
#         '低价': '低',
#         '新上市': '新上市',
#         '未上市': '未上市',
#         '买入': '买入',
#         '自选202307': None,
#         '测试20230516': None,
#     }
#
#     for key, value in tmp.items():
#         if key in tags_list:
#             if value is not None:
#                 list0.append(value)
#             tags_list.pop(tags_list.index(key))
#
#     for value in tags_list:
#         list0.append(value)
#
#     mark = load_json_txt("../basicData/self_selected/gui_mark.txt", log=False).get(code)
#     if mark is not None:
#         txt2 = txt2 + '-%s' % mark
#
#     data = self.counter_info
#     if isinstance(data, list):
#         txt_counter = '%s次/%.2f%%[%s]' % (data[2], data[4]*100, data[0])
#     else:
#         txt_counter = '%s次/%.2f%%[%s]' % (data, np.inf, '')
#
#     # list0.append('%.2f%%%s' % (self.max_increase_30*100, self.get_sign(self.max_increase_30)))
#
#     rate_tmp = load_json_txt("../basicData/self_selected/gui_rate.txt", log=False).get(code)
#     if rate_tmp is not None:
#         list0.append('%s%%+%.1f' % (rate_tmp, self.dividend_return))
#         rate_tmp = int(rate_tmp)
#     else:
#         rate_tmp = np.nan
#     rate_adj = 0 if pd.isna(rate_tmp) else rate_tmp
#     rate_adj = 25 if rate_adj > 25 else rate_adj
#     predict_rate = rate_adj * self.predict_delta / 36500 + 1
#
#     predict_profit = self.profit_salary_min * predict_rate
#     predict_discount = predict_profit / self.real_cost / 1e7
#     txt2 = txt2 + '-%.2f' % predict_discount
#
#     discount_index = np.log(predict_discount / 9) / np.log(1.2)
#     if not pd.isna(discount_index):
#         tmp0 = '-' if discount_index < 0 else ''
#         tmp1 = int(abs(discount_index))
#         tmp2 = int((abs(discount_index) % 1) * 12)
#
#         tmp2 = '%s个月' % tmp2 if tmp1 == 0 or tmp2 != 0 else ''
#         tmp1 = '%s年' % tmp1 if tmp1 != 0 else ''
#         txt2 = txt2 + '(%s%s%s)' % (tmp0, tmp1, tmp2)
#
#     if self.listing_date is not None:
#         list1.insert(0, self.listing_date)
#
#     list1.append(txt_counter)
#     list1.append('%.2f%%' % (self.yesterday_rise * 100))
#
#     ass = None
#     path = "../basicData/self_selected/gui_assessment.txt"
#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         value_dict = json.loads(f.read())
#         ass_str = value_dict.get(code)
#         if ass_str is not None:
#             try:
#                 ass = int(ass_str)
#             except Exception as e:
#                 print(e)
#
#     predict_ass = None if ass is None else ass * predict_rate
#
#     if ass is not None:
#         # ass2 = ass + self.liquidation_asset
#         cost = self.equity - self.liquidation_asset
#
#         rate = self.market_value / (predict_ass * 2 - cost) * 2
#         rate1 = (1/((rate/2) ** 0.1)-1) * 100
#
#         list0.append('%.2f' % rate)
#
#         rate = self.market_value / (predict_ass * 2 + self.liquidation_asset) * 2
#         rate2 = (1/((rate/2) ** 0.1)-1) * 100
#         txt_bottom1 = '%.0f/%.0f%+.0f%+.0f[%+.1f%%]/[%+.1f%%]' % (
#             self.market_value,
#             predict_ass,
#             self.liquidation_asset/2,
#             -self.equity/2,
#             rate2,
#             rate1,
#         )
#         list0.append('%.2f' % rate)
#
#         rate = ass / self.equity
#         list0.append('%.2f' % rate)
#     else:
#         txt_bottom1 = '%s%.2f亿' % ('cost: ', self.real_cost)
#
#     # if ass is not None:
#     #     rate = self.turnover / 1e6 / predict_ass
#     #     # txt2 = txt2 + '-%.2f‰' % rate
#     #     list0.insert(0, '%.2f‰' % rate)
#
#     txt3 = '/'.join(list0)
#     txt_bottom2 = '/'.join(list1)
#
#     GuiLog.add_log('show stock --> ' + txt1)
#     self.head_label1.setText(txt1)
#     self.head_label2.setText(txt2)
#     self.head_label3.setText(txt3)
#
#     self.bottom_label1.setText(txt_bottom1)
#     self.bottom_label2.setText(txt_bottom2)
#
#     if code not in self.show_list:
#         self.show_list.insert(0, code)
#         self.show_list = self.show_list[:5]
#
#     self.draw_left_pad()
#     self.pad_l.setPixmap(self.pad_l_pix)
#     # self.pad_r.setPixmap(self.pad_r_pix)
