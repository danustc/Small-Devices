import numpy as np
import pandas as pd
from os.path import join, dirname, abspath
import xlrd

def parse_xls(fpath):
    '''
    load the xls data.
    export: a data frame (in pandas)
    '''
    book = xlrd.open_workbook(fpath)
    sheet_names = book.sheet_names()
    print("sheet_names:", sheet_names)
    xl_sheet = book.sheet_by_name(sheet_names[0])
    title_row = xl_sheet.row_values(0) # title row
    print(title_row)
    xls_file = pd.ExcelFile(fpath)
    sht1 = xls_file.sheet_names[0]
    df = xls_file.parse(sht1)
    print(df.ix[0])
    print(df.ix[1])
    print(df[3:])
