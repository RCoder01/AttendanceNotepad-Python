import csv
from datetime import datetime
import os

import numpy
import pandas as pd

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

def get_repeat_num(head, list):
    add = ['', 0]
    while head + add[0] in list:
        add[1] += 1
        add[0] = ' (' + str(add[1]) + ')'
    return head + add[0]

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
            #out_df.reindex(sort_members(member_df).index)
            continue
    return True

def sort_key(series):
    if series.name == 'Grade':
        return series == 9
    string = series.str
    return string[:string.find(' ')] + string[string.find(' ') + 1:]

def sort_members(df):
    try:
        return df.sort_values(['Grade', 'Full Name'], key=sort_key)
    except KeyError:
        print('The "Member List" file was improperly formatted')

def get_members():
    try:
        return pd.read_csv(os.getcwd() + '\\Member List.csv').set_index('ID')
    except FileNotFoundError:
        print('The "Member List" file has either been removed or renamed')
        quit()

def get_output_table():
    file_path = os.getcwd() + '\\Output Table.csv'
    if os.path.isfile(file_path):
        try:
            return pd.read_csv(file_path)
        except pd.errors.EmptyDataError as err:
            pass
    open(file_path, 'w').close()
    return get_members().drop(columns=['Grade'])

def format_output_table(csv_table, member_table):
    csv_table = pd.merge(
        csv_table, 
        member_table.drop(columns=['Grade']),
        how='right', 
        on=['ID', 'Full Name']
    )
    return csv_table.assign(
        **{
            get_repeat_num(
                datetime.now().isoformat()[:10], 
                csv_table.columns
            ): [False for _ in range(len(csv_table))]
        }
    )

if __name__ == '__main__':
    mem = get_members()
    out = get_output_table()
    out2 = format_output_table(out, mem)