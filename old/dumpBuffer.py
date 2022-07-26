
# @log_it(None)
# def dump_res2buffer(res, stock_code, data_type):
#     time_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
#
#     if data_type == 'fs':
#         file = 'fs_data_%s_%s' % (stock_code, time_str)
#         path = '..\\bufferData\\buffer\\fs_buffer\\' + file
#
#     elif data_type == 'mvs':
#         file = 'mvs_data_%s_%s' % (stock_code, time_str)
#         path = '..\\bufferData\\buffer\\mvs_buffer\\' + file
#
#     else:
#         return
#
#     MainLog.add_log('    filepath --> %s' % path)
#     with open(path, 'wb') as pk_f:
#         pickle.dump(res, pk_f)
#
#     return path


# def get_files_by_datetime(dir_path, datetime):
#     list0 = [x for x in os.listdir(dir_path) if os.path.isfile(dir_path + x)]
#
#     file_list = list()
#     for file in list0:
#         file_path = '\\'.join([dir_path, file])
#         t0 = dt.datetime.fromtimestamp(os.path.getctime(file_path))
#         delta = (t0 - datetime).days
#         # print(type(delta), delta)
#         if delta >= 0:
#             file_list.append(file)
#     return file_list
#
# def buffer_files2mysql(datetime):
#     dir_path = '..\\bufferData\\financialData\\'
#     file_list = get_files_by_datetime(dir_path, datetime)
#
#     date_str = dt.date.today().strftime("%Y%m%d")
#     new_dir = '..\\bufferData\\fsData_updated\\fsData_update_%s\\' % date_str
#     if not os.path.exists(new_dir):
#         os.makedirs(new_dir)
#         MainLog.add_log('    make dir --> %s' % new_dir)
#
#     db, cursor = get_cursor('fsData')
#
#     # new_list = list()
#     for file in file_list:
#
#         stock_code = file[15:21]
#         file_path = dir_path + file
#
#         new_data = buffer2mysql(
#             path=file_path,
#             db=db,
#             cursor=cursor,
#             stock_code=stock_code,
#             data_type='fs',
#         )
#
#         # if len(new_data.index) == 0:
#         #     new_list.append((file, new_data))
#
#         MainLog.add_log('move file: ' + file_path + '-->' + new_dir)
#         shutil.move(file_path, new_dir)
#         MainLog.add_log('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
#
#     db.close()


# @log_it(None)
# def buffer2mysql(path, db, cursor, stock_code, data_type, res=None):
#
#     MainLog.add_log('    read buffer %s' % path)
#     MainLog.add_log('    stock_code --> %s' % stock_code)
#
#     if res is None:
#         with open(path, 'rb') as pk_f:
#             res = pickle.load(pk_f)
#
#     header_df = get_header_df(data_type)
#
#     if data_type == 'fs':
#         df = res2df_fs(res=res, header_df=header_df)
#         table = 'fs_%s' % stock_code
#         check_field = 'standardDate'
#
#     elif data_type == 'mvs':
#         df = res2df_mvs(res=res, header_df=header_df)
#         table = 'mvs_%s' % stock_code
#         check_field = 'date'
#
#     else:
#         return
#
#     MainLog.add_log('    table --> %s' % table)
#
#     header_str = sql_format_header_df(header_df)
#
#     # cursor.execute(sql_format_drop_table(table, if_exists=True))
#     # db.commit()
#
#     cursor.execute(sql_format_create_table(table, header_str))
#     db.commit()
#
#     df.drop(['first_update', 'last_update'], axis=1, inplace=True)
#
#     new_data = update_df2sql(
#         cursor=cursor,
#         table=table,
#         df_data=df,
#         check_field=check_field,
#         # ini=True,
#         ini=False,
#     )
#
#     if len(new_data.index) == 0:
#         MainLog.add_log('    new data: None')
#         return
#     else:
#         MainLog.add_log('    new data:\n%s' % repr(new_data))
#
#     return new_data
#
#
# def move_buffer_file(path, data_type):
#     date_str = dt.date.today().strftime("%Y%m%d")
#     if data_type == 'fs':
#         new_dir = '..\\bufferData\\updated\\fs\\date_%s\\' % date_str
#     elif data_type == 'mvs':
#         new_dir = '..\\bufferData\\updated\\mvs\\date_%s\\' % date_str
#     else:
#         return
#
#     if not os.path.exists(new_dir):
#         os.makedirs(new_dir)
#         MainLog.add_log('make dir --> %s' % new_dir)
#
#     MainLog.add_log('move file: %s --> %s' % (path, new_dir))
#     shutil.move(path, new_dir)