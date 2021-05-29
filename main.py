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


def output(str):
    print(str)

def handleError(str):
    output(str)
    quit()

def log(str):
    pass

def get_next_ID():
    while True:
        try:
            return int(input('id:\n'))
        except ValueError:
            output('Invalid ID input')

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
        handleError('The "Member List" file was improperly formatted')

def get_members():
    try:
        return pd.read_csv(os.getcwd() + '\\Member List.csv').set_index('ID')
    except FileNotFoundError:
        handleError('The "Member List" file has either been removed or renamed')

def get_output_table():
    file_path = os.getcwd() + '\\Output Table.csv'
    if os.path.isfile(file_path):
        try: return pd.read_csv(file_path)
        except pd.errors.EmptyDataError as err: pass
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
            ): [False] * len(csv_table)
        }
    )

def format_session_table(member_table):
    ses = member_table.copy()
    cols = [
        ['Times', list],
        ['Total Seconds', lambda: 0.0],
        ['Credit', lambda: False],
    ]
    for name, val in cols:
        ses[name] = [val() for _ in range(len(member_table))]
    return ses

def read_cfgs():
    cfg_dict = {
        'requiredHours': 2
    }
    try:
        with open('config.cfg', encoding='UTF-8') as cfg_file:
            for line in cfg_file.readlines():
                if line.find('=') != -1:
                    opt, val = line.replace('\n', '').split('=', 1)
                    try: val = eval(val)
                    except NameError: pass
                    except SyntaxError: pass
                    cfg_dict[opt] = val
    except FileNotFoundError:
        open('config.cfg', mode='x', encoding='UTF-8').close()
    return cfg_dict

def sign_in_out(ID, session_df):
    session_df.at[ID, 'Times'] += [datetime.now()]
    time_list = session_df.at[ID, 'Times']
    if len(time_list) % 2:
        session_df.at[ID, 'Total Seconds'] += time_list[-2] - time_list[-1]
        return True
    return False

if __name__ == '__main__':
    mem = sort_members(get_members())
    out = format_output_table(get_output_table(), mem)
    ses = format_session_table(mem)
    cfgs = read_cfgs()

    while True:
        ID = get_next_ID()
        if ID not in mem.index:
            output(str(ID) + ' not found in the Member List, please try again')
            continue
        io = ['out', 'in'][sign_in_out(ID, ses)]
        output(f'You have successfully signed {io}!')
        log(f'{ID} signed {io}')
