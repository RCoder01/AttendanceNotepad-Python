import csv
from datetime import datetime
import os

import numpy
import pandas


months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]

def get_next_ID():
    return input('id:\n')

def write_final(data):
    for rel_path, ext in [('\\files\\logs', 'txt'), ('\\files\\tables', 'csv')]:
        now = datetime.now()
        out_dir = f'{os.getcwd()}{rel_path}\\{now.year}\\{months[now.month - 1]}'
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        add = ['', 0]
        while not os.path.isfile(f'{out_dir}\\{now.date}{add[0]}.{ext}'):
            add[1] += 1
            add[0] = ' (' + add[1] + ')'

        if ext == 'txt':
            continue
        if ext == 'csv':
            continue
    return True


def sort_key(series):
    if series.name == 'Grade':
            return series == 9
    return series

def sort_members(member_list_dataframe):
    for i in member_list_dataframe.index:
	member_list_dataframe['Sorted Name'][i] = member_list_dataframe['Sorted Name'][i][1] + member_list_dataframe['Sorted Name'][i][0]
    return df.sort_values(['Grade', 'Sorted Name'], key=sort_key)
