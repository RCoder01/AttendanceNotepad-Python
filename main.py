import collections
import csv
from datetime import datetime, timedelta
import os

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.series import Series

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


def output(str: str) -> None:
    print(str)


def handleError(str: str) -> None:
    output(str)
    quit()


def log(str: str, log_list: list) -> list:
    """Appends a timestamped str to log_list"""
    
    log_list.append(f'[{datetime.now().isoformat()}] {str}')
    return log_list


def get_next_ID() -> int:
    """Returns a user input for the next ID to be processed"""
    
    while True:
        try:
            return int(input('id:\n'))
        except ValueError:
            output('Invalid ID input')


def get_repeat_num(head: str, list: list) -> str:
    """Calculates modifier for head such that it is unique in list"""

    add = ['', 0]
    while head + add[0] in list:
        add[1] += 1
        add[0] = ' (' + str(add[1]) + ')'
    return head + add[0]


def write_session(log_list: list, ses_df: DataFrame) -> None:
    """Writes the log and csv output files specified by the given data"""

    #Runs for log and table
    for rel_path, ext in [
            ('\\files\\logs', 'txt'), 
            ('\\files\\tables', 'csv'),
        ]:
        now = datetime.now()

        out_dir = os.getcwd() \
                   + rel_path \
                   + '\\' \
                   + str(now.year) \
                   + '\\' \
                   + months[now.month - 1]
        #Creates output_directory if it doesn't already exist
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        #Output file name with relative directory
        out_path = out_dir \
             +  '\\' \
             +  get_repeat_num(
                    str(now.day), 
                    [
                        os.path.splitext(file)[0] 
                        for file 
                        in os.listdir(out_dir)
                    ]
                ) \
             +  '.' \
             +  str(ext)
        
        #Handling for logs
        if ext == 'txt':
            with open(out_path, mode='w', encoding='UTF-8') as f:
                for line in log_list:
                    f.write(line + '\n')
            continue
        
        #Handling for tables
        elif ext == 'csv':
            #Formats ses_df (session_dataframe) for output
            ses_df_copy = ses_df.copy()
            ses_df_copy['Credit'] = ses_df['Credit'].astype(int)
            ses_df_copy['Times'] = ses_df['Times'].apply(
                lambda x: [str(e) for e in x]
            )
            ses_df_copy['Total Time'] = ses_df_copy['Total Time'].map(
                timedelta.total_seconds
            )
            ses_df_copy['Total Time'] /= 3600
            ses_df_copy = ses_df_copy.rename(
                columns={
                    'Total Time': 'Hours Spent'
                }
            )
            
            #Writes modified copy of ses_df
            ses_df_copy.to_csv(out_path)
            continue


def sort_key(series: Series) -> Series:
    """Robostangs attendance sorting algorithm"""

    #For the grade column, sort new members last (True sorts after False)
    if series.name == 'Grade':
        return series == 9

    #For 'Full Name', sort alphabetically by last, then first name
    string = series.str
    return string[:string.find(' ')] + string[string.find(' ') + 1:]


def sort_members(member_df: DataFrame) -> DataFrame:
    """Sorts member_df using defined key 'sort_key'"""

    try:
        return member_df.sort_values(['Grade', 'Full Name'], key=sort_key)
    except KeyError:
        handleError('The "Member List" file was improperly formatted')


def get_members() -> DataFrame:
    """Returns a dataframe of the data in local 'Member List.csv'"""

    try:
        return pd.read_csv(os.getcwd() + '\\Member List.csv').set_index('ID')
    except FileNotFoundError:
        handleError('The "Member List" file has either been removed or renamed')


def get_output_table() -> DataFrame:
    """Returns dataframe of existing data in local 'Output Table.csv'
    If no file exists, creates one and returns a base dataframe
    """

    file_path = os.getcwd() + '\\Output Table.csv'
    
    #If the file exists
    if os.path.isfile(file_path):
        try:
            return pd.read_csv(file_path).set_index('ID')
        #If file is empty, continue and return base dataframe
        except pd.errors.EmptyDataError as err:
            pass
    
    #If either the file does not exist or the file is empty
    open(file_path, 'w').close()
    return get_members().drop(columns=['Grade'])


def format_output_table(
        csv_df: DataFrame, 
        member_df: DataFrame
    ) -> DataFrame:
    """Returns a properly formatted csv_table"""

    #Technically a one-liner
    #First, merges csv_table and member_table such that:
    #   Members removed from member_table are removed
    #   Members added to member_table are added
    #Next, adds a new column for this session and populates with False
    return pd.merge(
        csv_df, 
        member_df.drop(columns=['Grade']),
        how='right', 
        on=['ID', 'Full Name']
    ).assign(
        **{
            get_repeat_num(
                datetime.now().isoformat()[:10], 
                csv_df.columns
            ): [False] * len(csv_df)
        }
    )


def format_session_table(member_df: DataFrame) -> DataFrame:
    """Returns a new session table instance"""

    ses = member_df.copy()
    #Columns with names and data value functions
    cols = [
        ['Times', list],
        ['Total Time', timedelta],
        ['Credit', lambda: False],
    ]
    #Adds and populates columns
    for name, val in cols:
        ses[name] = [val() for _ in range(len(member_df))]
    
    return ses


def read_cfgs() -> dict:
    """Returns a config dictionary from local 'configs.cfg'"""

    cfg_file_name = 'config.cfg'
    #Default configs
    cfg_dict = {
        'requiredHours': 2
    }

    try:
        with open(cfg_file_name, encoding='UTF-8') as cfg_file:
            for line in cfg_file.readlines():
                if line.find('=') != -1:
                    #For valid lines in 'config.cfg' with an '='
                    opt, val = line.replace('\n', '').split('=', 1)
                    #Try to convert the value (after '=') to a number
                    try:
                        val = eval(val)
                    except NameError:
                        pass
                    except SyntaxError:
                        pass
                    #If it's not a number, just add as string
                    cfg_dict[opt] = val
    #If config.cfg doesn't exist, create it
    except FileNotFoundError:
        open('config.cfg', mode='x', encoding='UTF-8').close()
    
    return cfg_dict


def sign_in_out(ID: int, session_df: DataFrame, reqd_hours: int) -> bool:
    """
    Modifies session_df as necessary for sign-ins and outs and logs.
    
    Saves current time to ID's 'Times' array.
    If it's a sign out, updates time spent at meeting.
    Returns True if event is a sign-in, False if sign-out.
    """

    #Add now to the list of times signed in/out
    session_df.at[ID, 'Times'] += [datetime.now()]

    time_list = session_df.at[ID, 'Times']
    #If event is a sign out
    if not (len(time_list) % 2):
        #Adds timedelta to total time
        session_df.at[ID, 'Total Time'] += time_list[-1] - time_list[-2]
        #Updates credit if timedelta total is enough
        session_df.at[ID, 'Credit'] = \
            session_df\
                .at[ID, 'Total Time']\
                .total_seconds() \
             > reqd_hours * 3600
        
        return False
    return True


if __name__ == '__main__':
    #Initialize all dataframes and log list
    mem = sort_members(get_members())
    out = format_output_table(get_output_table(), mem)
    ses = format_session_table(mem)
    cfgs = read_cfgs()
    log_list = []

    #Gets ID input and runs until keyboard interrupt
    try:
        while True:
            ID = get_next_ID()
            
            if ID not in mem.index:
                output(str(ID) + ' not found in the Member List, please try again')
                continue
            
            #Uses sign_in_out output to determine sign-in or sign-out
            io = ['in', 'out'][not sign_in_out(ID, ses, cfgs['requiredHours'])]
            
            output(f'You have successfully signed {io}!')
            log(f'{ID} signed {io}', log_list)
    #Exits infinite loop on keyboard interrupt
    except KeyboardInterrupt:
        print('Ending')
    
    #Converts 'Credit' column from boolean to int for convenience
    out[out.columns[-1]] = ses['Credit'].astype(int)

    #Writes final outputs
    write_session(log_list, ses)
    out.to_csv(f'Output Table.csv')