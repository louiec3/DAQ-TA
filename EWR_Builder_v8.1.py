import pandas as pd
import numpy as np
import re as re
import os
from os.path import dirname, abspath 
from tkinter import *
from tkinter import ttk, filedialog, messagebox, simpledialog
import itertools

version_num = 'v8'
release_date = 'February 22, 2022'

root = Tk()
root.title('EWR Builder - ' + version_num)

window_height = 700
window_width = 800

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_coordinate = int((screen_width/2) - (window_width/2))
y_coordinate = int((screen_height/2) - (window_height/2))

root.geometry('{}x{}+{}+{}'.format(window_width, window_height, x_coordinate, y_coordinate))

# root.geometry('500x500') # use this if above doesnt work
root.pack_propagate(False)

## Global Variables Start

# Used in Paste Data page
path_script = dirname(__file__) + '\\'
print('Path of EWR Builder: ' + path_script)
path_temp = path_script + 'temp_EWR.csv'

# POR Toggle variable: used in Import File and Paste Data page
# Use these values to change checkbox defaults 
checkbox_por_state = IntVar(value=1)
checkbox_truncate_state = IntVar(value=1)
checkbox_sort_state = IntVar(value=0)
option_letter_case = StringVar()
# The default ordering of the Letter Casing option can be changed in line...
# CTRL + F 
# option_letter_case.set(case_options[0])
# Then change the value between the brackets to reflect the default value. 0, 1, or 2
## Global Variables End


def remove_whitespace(dataframe): ## Short desc is created twice on complete EWRs
    try:
        dataframe['SHORTDESC'] = dataframe['SHORTDESC'].replace(r'^\s*$', np.nan, regex=True)
        dataframe['SHORTDESC'] = dataframe['SHORTDESC'].str.strip()
        dataframe['SHORTDESC'] = dataframe['SHORTDESC'].fillna(value='uncertain')
    except KeyError:
        messagebox.showerror('Error', 'One or both files do not contain a SHORTDESC column.\n'
        'Please check that you are using complete EWRs or use the Import File page to validate your files.')
        return

def nan_rows_calculate(df):
    global DF_NAN_ROWS

    DF_NAN_ROWS = df[df.isnull().any(axis=1)].copy()
    DF_NAN_ROWS['Row#'] = DF_NAN_ROWS.index.values
    DF_NAN_ROWS.reset_index(drop=True, inplace=True)
    DF_NAN_ROWS['Row#'] = DF_NAN_ROWS['Row#'] + 2
    cols_df_nan = DF_NAN_ROWS.columns.tolist()
    cols_df_nan = cols_df_nan[-1:] + cols_df_nan[:-1]
    DF_NAN_ROWS = DF_NAN_ROWS[cols_df_nan]
    DF_NAN_ROWS = DF_NAN_ROWS.to_string(index=False)


def shortdesc_validation(dataframe,originaldesc_list,newdesc_list):
    global TRUNC_DICT
    ## checks if any of the non-unique truncated descriptions and renames them
    ## Initialising dictionary
    desc_zip = zip(originaldesc_list, newdesc_list)
    desc_dict = dict(desc_zip)
    ## Look for duplicate values
    dupcounter_dict = {value: itertools.count() for value in desc_dict.values()}

    newdesc_dict = {key: (lambda x: value if not x else value[:15] + str(x))(next(dupcounter_dict[value])) for key, value in desc_dict.items()}
    dataframe['SHORTDESC'] = dataframe['SHORTDESC'].replace(newdesc_dict) 

    # Check if descriptions were manipulated
    TRUNC_DICT = {}
    for key, value in newdesc_dict.items():
        if value != key:
            TRUNC_DICT[key] = value


## F04
def cellno_assign(dataframe, t_f_removal):
        global NUM_TOTAL_CELLS
        
        shortdesc_list = dataframe['SHORTDESC'].unique().tolist()
        shortdesc_list = sorted(shortdesc_list)
        
        if 'uncertain' in shortdesc_list:
            shortdesc_list.remove('uncertain')
            shortdesc_list.append('uncertain')
            
        max_cellno = 100
        shortdesc_count = len(shortdesc_list)

        if t_f_removal is False:
            print('Creating EWR...')
            if checkbox_por_value() == 0:
                if 'por' in shortdesc_list:
                    shortdesc_list.remove('por')
                    shortdesc_list.insert(0, 'por')
        elif t_f_removal is True:
            print('Merging EWR...')
            if 'por' in shortdesc_list: ## tests if por should be cellno 0 or alphanumeric sort
                print(dataframe.loc[dataframe['SHORTDESC'] == 'por', 'CELLNO'].iloc[0])
                por_cellno = dataframe.loc[dataframe['SHORTDESC'] == 'por', 'CELLNO'].iloc[0]
                if por_cellno == '0':
                    print('Por CellNo: ' + str(por_cellno))
                    shortdesc_list.remove('por')
                    shortdesc_list.insert(0, 'por')
        if shortdesc_count > max_cellno:
            messagebox.showerror('Error', 'The provided file is not compatible. Too many cell numbers: ' + str(shortdesc_count))
        else:
            dataframe['CELLNO'] = dataframe['SHORTDESC'].apply(lambda x: shortdesc_list.index(x) if x != '' else 'uncertain')
            
            NUM_TOTAL_CELLS = str(len(dataframe['CELLNO'].unique()))
        return dataframe
    

def checkbox_por_value():
    if checkbox_por_state.get() == 1:
        print('EWR', 'POR will start at 0.')
        return 0
    elif checkbox_por_state.get() == 0:
        print('EWR', 'POR will start at 1.')
        return 1


def checkbox_sort_value(df):
    if checkbox_sort_state.get() == 1:
        df = df.sort_values('WAFERID').reset_index(drop=True)
        print('EWR', 'Wafer IDs will be sorted alphanumerically.')
        return 0
    elif checkbox_sort_state.get() == 0:
        print('EWR', 'Wafer IDs will not be sorted.')
        return 1


## notes for future:
## Nested functions are unnesessary...
## Next time, create a function to run all the other functions
## This should make the code more dynamic as it can take variables 
## as an input
## Should reduce the need for global variables.

def ewr_create(path, t_f_import):


    ## F02
    def shortdesc_format():
        global TRUNC_DICT
        if option_letter_case.get() == 'Lower case':
            DF_INPUT['SHORTDESC'] = DF_INPUT['SHORTDESC'].str.casefold()
            DF_INPUT['LONGDESC'] = DF_INPUT['LONGDESC'].str.casefold()
        elif option_letter_case.get() == 'Upper case':
            DF_INPUT['SHORTDESC'] = DF_INPUT['SHORTDESC'].str.upper()
            DF_INPUT['LONGDESC'] = DF_INPUT['LONGDESC'].str.upper()
        elif option_letter_case.get() == 'Preserve case (long desc. only)':
            DF_INPUT['SHORTDESC'] = DF_INPUT['SHORTDESC'].str.casefold()
            DF_INPUT['LONGDESC'] = DF_INPUT['LONGDESC']


        if checkbox_truncate_state.get() == 1:
            longdesc_list = DF_INPUT['LONGDESC'].unique().tolist()
            shortdesc_list = DF_INPUT['LONGDESC'].unique().tolist()
            shortdesc_list = [desc.replace(' ','') if len(desc) > 16 else desc for desc in shortdesc_list]
            shortdesc_list = [desc.replace('-','') if len(desc) > 16 else desc for desc in shortdesc_list]
            shortdesc_list = [desc.replace('_','') if len(desc) > 16 else desc for desc in shortdesc_list]
            shortdesc_list = [desc[:16] if len(desc) > 16 else desc for desc in shortdesc_list]
            
            shortdesc_validation(DF_INPUT, longdesc_list, shortdesc_list)

    # shortdesc_format()


    ## F04 ## Above ewr_create()


    ## F05
    ## Issue with CT_etch_chamber_information.xlsx
    def waferid_identify():
        global t_f_WAFERID_COL
        
        waferid_full_template1 = '[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]-[0-2][0-9]'
        waferid_full_template2 = '[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]-[0-2][0-9]'
        waferid_partial_full_template = '[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]-[0-9]'

        columns = DF_INPUT.columns
        df_length = len(DF_INPUT)
        print('Searching for WaferID col...')
        
        for column in columns[:-1]:
            DF_INPUT[column] = DF_INPUT[column].astype(str)
            i = 0
            for row in DF_INPUT[column]:
                if re.search(waferid_full_template1, row) or re.search(waferid_full_template2, row) or re.search(waferid_partial_full_template, row):
                    i += 1
            if i == df_length:
                t_f_WAFERID_COL = True
                DF_INPUT['WAFERID'] = DF_INPUT[column].str.upper()
                return True
            else:
                t_f_WAFERID_COL = False
        try:
            if t_f_WAFERID_COL is False:
                print('WaferID col not found...')
        except:
            messagebox.showerror('EWR Builder', 'Error occured while identifying WaferID column.')
            return None
    #waferid_identifyv4()


    ## F18
    def wafernum_identify():
        global t_f_WAFERNUM_COL
        
        if t_f_WAFERID_COL is True:
            t_f_WAFERNUM_COL = False
            return
        
        wafernum = '^[0-1][0-9]$'
        wafernum_max = '^[2][0-5]$'
        wafernum_overflow1 = '^[2][6-9]$' ## These overflow regex could probably be simplified...
        wafernum_overflow2 = '^[3-9][0-9]$'
        wafernum_overflow3 = '^[0-9][0-9][0-9]$'
        wafernum_partial = '^[0-9]$'
        
        columns = DF_INPUT.columns
        df_length = len(DF_INPUT)
        
        print('Searching for WaferNum col...')
        
        for column in columns[:-1]:
            DF_INPUT[column] = DF_INPUT[column].astype(str)
            i = 0
            for row in DF_INPUT[column]:
                if re.search(wafernum, row) or re.search(wafernum_max, row) or re.search(wafernum_partial, row):
                    i += 1
                if re.search(wafernum_overflow1, row) or re.search(wafernum_overflow2, row) or re.search(wafernum_overflow3, row):
                    messagebox.showerror('EWR Builder', 'One or more Wafer IDs exceed the 25 threshold.')
                    return      
            if i == df_length:
                t_f_WAFERNUM_COL = True
                DF_INPUT['WAFERID'] = DF_INPUT[column]
                return True
            else:
                pass
                t_f_WAFERNUM_COL = False
        if t_f_WAFERNUM_COL is False:
            print('WaferNum col not found.')
    # wafernum_identify()


    ## F06 ## Works
    def wafernum_format(): # Based on output of waferid_identify func (f6)
        print('Formatting...')
        DF_INPUT['WAFERID'] = DF_INPUT['WAFERID'].apply(lambda row: row.zfill(2))
    
    # wafernum_format()


    ## F07 ## Works
    def combine_lotid_wafernum(): # Based on output of waferid_identify
        DF_INPUT['WAFERID'] = DF_INPUT['#LOTID'].apply(lambda row: row[0:5]) + '-' + DF_INPUT['WAFERID'].str.upper() #.astype(str)
    
    # combine_lotid_wafernum()


    ## F08
    def lotid_identifyv2():
        global t_f_LOTID_COL
        
        extra_chars = ['_', '-', ' ']
        lotid_full_template = '^[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]\.[1]$'
        lotid_5 = '^[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]$'
        lotid_6 = '^[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]$'
        lotid_5_dot_num = '^[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]\.[1]'
        lotid_6_dot_num = '^[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]\.[1]'
        
        columns = DF_INPUT.columns
        df_length = len(DF_INPUT)
        
        print('Searching for LOTID col...')
        
        for column in columns[:-1]:
            i = 0
            for row in DF_INPUT[column]:
                if re.search(lotid_full_template, row):
                    i += 1
                elif re.search(lotid_5, row) or re.search(lotid_6, row) or re.search(lotid_5_dot_num, row) or re.search(lotid_6_dot_num, row):
                    if len(row) <= 10:
                            if len(row) >= 5:
                                if any(char in row for char in extra_chars):
                                    pass
                                else:
                                    i += 1
            print('Lot IDs found: ' + str(i) + 'out of ' + str(df_length))
            if i == df_length:
                t_f_LOTID_COL = True
                DF_INPUT['#LOTID'] = DF_INPUT[column]
                return 
            else:
                t_f_LOTID_COL = False
        if t_f_LOTID_COL is False:
            print('LOTID col not found.')
    
    # lotid_identifyv2()


    ## F09 ## Works
    def lotid_format(): ## ** use as a global function (merge shortdesc)
        DF_INPUT['#LOTID'] = DF_INPUT['#LOTID'].apply(lambda row: row[0:5] + '.1')
        DF_INPUT['#LOTID'] = DF_INPUT['#LOTID'].str.upper()
    
    # lotid_format()


    ## F11
    # def dup_rows():
    #     global DF_INPUT
    #     DF_INPUT = DF_INPUT.drop_duplicates(keep='last', ignore_index=True)
    #     #print(df)
    
    # #dup_rows()


    ## F12
    def dup_waferids():
        global DF_INPUT
        global NUM_DUP_WAFERIDS
        global DF_DUP_ROWS
        
        DF_DUP_ROWS = DF_INPUT[DF_INPUT.duplicated(['WAFERID'], keep='last')]
        DF_INPUT.columns.names = ['Row#']
        dup_waferids_initial = len(DF_INPUT)
        DF_INPUT = DF_INPUT.drop_duplicates(keep='last', ignore_index=True)
        DF_INPUT = DF_INPUT.drop_duplicates(subset=['WAFERID'], keep='last')
        DF_INPUT = DF_INPUT.reset_index()
        dup_waferids_final = len(DF_INPUT)
        NUM_DUP_WAFERIDS = dup_waferids_initial - dup_waferids_final
        NUM_DUP_WAFERIDS = str(NUM_DUP_WAFERIDS)

    # dup_waferids()


    ## F15 -> remove_wafers_confirm()
    ## inside GUI functions


    ## F16 coded within F02


    ## F17
    def verify_headers():
        global DF_INPUT
        
        wafernum_template = '^[0-9]$|^[0-2][0-9]$'
        waferid_full_template1 = '[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]-[0-2][0-9]'
        waferid_full_template2 = '[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]-[0-2][0-9]'
        waferid_partial_full_template = '[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]-[0-9]'
        lotid_full_template1 = '[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9].[1]'
        lotid_full_template2 = '[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9].[1][a-zA-Z]'
        keywords = ['lotid', 'lot id', 'lot_id', 'lotid5', 'waferid', 'wafer_id', 'description', 'nickname', 
                    'shortdesc', 'cellno', 'longdesc', 'short desc', 'longdesc', 'lot', 'wafer', 'desc']
        ## more specfic keywords should be listed before less specfic keyword
        list_headers = DF_INPUT.columns.values.tolist()
        list_headers = [header.casefold() for header in list_headers]
        for keyword in keywords:
            for header in list_headers:
                if keyword in header:
                    return
            if (re.search(wafernum_template, header) or re.search(waferid_full_template1, header) or re.search(waferid_full_template2, header) or
                re.search(waferid_partial_full_template, header) or re.search(lotid_full_template1, header) or re.search(lotid_full_template2, header)):
                break
        ## add in temporary headers
        print('No header row.')
        DF_INPUT = DF_INPUT.columns.to_frame().T.append(DF_INPUT, ignore_index=True).reset_index(drop=True)
        DF_INPUT.columns = range(len(DF_INPUT.columns))  
        print(DF_INPUT)
        
        # verify_headers()


    def verify_first_row():
        global DF_INPUT
        
        list_headers = DF_INPUT.columns.values.tolist()
        list_unnamed_headers = []
        # print(list_headers)
        if 'Unnamed' in str(list_headers):
            for header in list_headers:
                list_unnamed_headers.append(header)
            if len(list_unnamed_headers) > 0:
                new_headers = DF_INPUT.iloc[0]
                DF_INPUT.columns = new_headers
                DF_INPUT = DF_INPUT[1:]
                DF_INPUT.reset_index(drop=True)
    
    #verify_first_row()


    ## F18 is below F05


    ## F19
    def longdesc():
        DF_INPUT['LONGDESC'] = DF_INPUT['SHORTDESC']
        # DF_INPUT['LONGDESC'] = DF_INPUT['LONGDESC'].str.casefold()
        # remove_whitespace(DF_INPUT)
    
    # longdesc()

    ## F20
    def waferid_format():
        waferid_list = DF_INPUT['WAFERID'] #.tolist()
        print('Wafer ID List:')
        print(waferid_list)
        i = 0
        for row in waferid_list:
            print(row)
            nums = row.split('-')[1] ## ** causes problem with complete EWRs (use-case: EWR format validation)
            chars = row.split('-')[0]
            if re.search('^[0-9]$', nums):
                nums = '0' + nums
                newid = chars + '-' + nums
                DF_INPUT.at[i, 'WAFERID'] = newid
            i += 1
    
    # waferid_format()


    ## F21
    def strip_lotid_from_waferid():
        DF_INPUT['#LOTID'] = DF_INPUT['WAFERID'].apply(lambda row: row[:5] + '.1')
    
    # strip_lotid_from_waferid()


    ## F22 Expand lotid to 25 wafers
    def expand_wafers_25():
        global DF_INPUT
        
        df_expanded = pd.DataFrame()
        lotid_list = DF_INPUT['#LOTID'].unique()
        num_unique_lotids = len(lotid_list)
        if num_unique_lotids == len(DF_INPUT):
            print('Expanding wafer IDs...')
            df_expanded = pd.DataFrame(np.repeat(DF_INPUT.values, 25, axis=0))
            df_expanded = df_expanded.iloc[:, [0, 1]]
            df_expanded.columns = ['#LOTID', 'SHORTDESC']
            df_expanded['WAFERID'] = 0
            i = 0
            k = 0
            while i < len(DF_INPUT) and k < len(df_expanded):
                j = 1
                while j < 26:
                    if i == 0:
                        df_expanded.at[k, 'WAFERID'] = j
                    elif i > 0:
                        df_expanded.at[k, 'WAFERID'] = j 
                    # print(j)
                    j += 1
                    k += 1
                i += 1
            DF_INPUT = df_expanded
            DF_INPUT['WAFERID'] = DF_INPUT['WAFERID'].astype(str)        
        else:
            print('Error at expand_wafers_25 function.') # this step shouldnt occur
    
    # expand_wafers_25()


    ## F23
    def dup_lotid():
        global DF_INPUT
        
        DF_INPUT = DF_INPUT.drop_duplicates(subset=['#LOTID'], keep='last')
        DF_INPUT = DF_INPUT.reset_index(drop=True)
    
    # dup_lotid()


    ## F24
    def drop_na():
        global DF_INPUT
        global NUM_NA_ROWS_TOTAL
        
        DF_INPUT.replace(r'^\s*$', np.nan, regex=True)
        DF_INPUT['SHORTDESC'] = DF_INPUT['SHORTDESC'].fillna(value='uncertain')
        na_rows_inital = len(DF_INPUT)
        DF_INPUT = DF_INPUT.dropna().reset_index(drop=True)
        na_rows_final = len(DF_INPUT)
        NUM_NA_ROWS_TOTAL =  na_rows_inital - na_rows_final
        NUM_NA_ROWS_TOTAL = str(NUM_NA_ROWS_TOTAL)
        print('N/A rows: ' + NUM_NA_ROWS_TOTAL) ## **Statistic Var
        
    global DF_NAN_ROWS
    global DF_EWR
    global EWR_filepath
    global NUM_UNIQUE_LOTIDS ## ** Statistic Var
    global NUM_UNIQUE_WAFERIDS ## ** Statistic Var
    global FILEPATH

    ## Begin EWR Creation   
    print('Input dataframe:')
    print(DF_INPUT)
    verify_first_row() 
    verify_headers()

    if 'SHORTDESC' not in DF_INPUT.columns:
        DF_INPUT.columns = [*DF_INPUT.columns[:-1], 'SHORTDESC']
        remove_whitespace(DF_INPUT)
        longdesc()

    nan_rows_calculate(DF_INPUT)
    drop_na()
    waferid_identify()
    lotid_identifyv2()
    wafernum_identify()

    print('WaferID col =  ' + str(t_f_WAFERID_COL))
    print('WaferNum col = ' + str(t_f_WAFERNUM_COL))
    print('LOTID col =    ' + str(t_f_LOTID_COL))
    print('\nShort descriptions:')
    print(DF_INPUT['SHORTDESC'])

    if t_f_WAFERID_COL is True:
        ## Assign cellID based on ShortDesc. Export.
        print('Wafer ID = true')
        waferid_format()
        strip_lotid_from_waferid()
        shortdesc_format()
        dup_waferids()
        cellno_assign(DF_INPUT, t_f_removal=False)

    elif t_f_LOTID_COL is False:
        ## Reformat LOTID and WaferID if needed. Combine them. Assign CellID based on ShortDesc. Export.
        messagebox.showerror('EWR Builder', 'File Failed. \nNo Lot ID or Wafer ID column was found. Ensure these columns exist or ' 
                            'check if these columns have a recognizable format.')
        print('Lot ID = false')
        return
        
    elif t_f_LOTID_COL is True and t_f_WAFERNUM_COL is True:
        print('Wafer Num = true, LOT ID = true')
        wafernum_format()
        lotid_format()
        combine_lotid_wafernum()
        shortdesc_format()
        dup_waferids()
        cellno_assign(DF_INPUT, t_f_removal=False)
        
    elif t_f_LOTID_COL is True and t_f_WAFERNUM_COL is False:
        ## Expand LOTIDs to 25. Format LOTIDs. Assign WaferID 01-25. Combine them. Assign CellID based on ShortDesc. Export.  
        print('Wafer Num = False, Lot ID = true')
        dup_lotid()
        lotid_format() ##09
        expand_wafers_25() ##22
        wafernum_format() ##06
        lotid_format() ##09
        combine_lotid_wafernum() ##07
        longdesc() ##Justin
        shortdesc_format()
        dup_waferids()
        cellno_assign(DF_INPUT, t_f_removal=False) ##F04
    
    else:
        print('The provided file is not compatible.')
        messagebox.showerror('Error', 'The provided file is not compatible.')
        return
    
    DF_EWR = DF_INPUT[['#LOTID', 'WAFERID', 'CELLNO', 'SHORTDESC', 'LONGDESC']]

    checkbox_sort_value(DF_EWR)
    
    print('Selected File: ' + path)
    
    if t_f_import is True:
        EWR_filepath = os.path.splitext(path)[0] + '_EWR.csv'

        while os.path.exists(EWR_filepath) is True or EWR_filepath == '':
            override_YN = messagebox.askquestion('EWR Builder', 'File already exists. Override?', parent=root)
            if override_YN == 'yes':
                break
            else:
                while os.path.exists(EWR_filepath) is True or EWR_filepath == '':
                    EWR_filepath = simpledialog.askstring('EWR Builder', 'File already exists. Enter a file name (do not add file extension):', parent=root).strip() 
                    EWR_filepath = dirname(path) + '/' + EWR_filepath + '_EWR.csv'
        
    else:
        EWR_filepath = path_script + '\\' + os.path.splitext(path)[0] + '_EWR.csv'
    
    print('Output file: ' + EWR_filepath)
    
    DF_EWR.to_csv(EWR_filepath, index=False)
    messagebox.showinfo('EWR Builder', 'Complete.\n\n' + 'The file has been saved to: \r' + EWR_filepath)
    
    trunc_list = []
    if TRUNC_DICT:
        for key, value in TRUNC_DICT.items():
            trunc_list.append(str(key) + ' -> ' + str(value))
            print(str(len(trunc_list)) + ' short descriptions were shortend: ', key, ' => ', value)
        messagebox.showinfo('EWR Builder', str(len(trunc_list)) + ' descriptions were shortened:\n\n' + '\n'.join(trunc_list))
    
    clear_data()

    NUM_UNIQUE_LOTIDS = str(len(DF_EWR['#LOTID'].unique()))
    NUM_UNIQUE_WAFERIDS = str(len(DF_EWR['WAFERID'].unique()))
    FILEPATH = None    
    
    return None


def remove_temp(path):
    if os.path.exists(path): ## remove temp file, block is used more than once
        os.remove(path)

def stats_general():
    global STAT1_LABEL
    global STAT2_LABEL
    global STAT3_LABEL
    global STAT4_LABEL
    global STAT5_LABEL
    
    try: 
        STAT1_LABEL['text'] = 'Total Lot ID5s: ' + NUM_UNIQUE_LOTIDS
        STAT2_LABEL['text'] = 'Total Wafer IDs: ' + NUM_UNIQUE_WAFERIDS
        STAT3_LABEL['text'] = 'Total Cells: ' + NUM_TOTAL_CELLS
        STAT4_LABEL['text'] = 'Duplicate Wafer IDs (last ID kept): ' + NUM_DUP_WAFERIDS
        STAT5_LABEL['text'] = 'Rows missing data (dropped): ' + NUM_NA_ROWS_TOTAL
    except NameError: 
        return None
        
## Main Menu Start

def main_btn():
    button_main = Button(root, text=' Main Menu ', command=lambda: main_menu_page())
    button_main.place(x=0, y=0)

def about_btn():
    button_about = Button(root, text=' About ', command=lambda: about_page())
    button_about.pack(side=TOP, anchor=NE)

def main_menu_page():
    for widget in root.winfo_children():
        widget.destroy()

    main_btn()
    about_btn()
    
    ## Frame for file dialog
    frame_main = LabelFrame(root, text='Text', font=18, bd=2, relief='ridge')
    frame_main.place(height=300, width=400, rely=0.5, relx=.5, y=-50, anchor=CENTER)

    page_title = Label(root, text='Main Menu')
    page_title.place(relx=.5, y=37, anchor=CENTER)
    page_title.config(font=('arial', 20))
    
    label1 = Label(frame_main, text='Select a button.')
    label1.place(rely=.15, relx=.5, anchor=CENTER)

    label2 = Label(frame_main, text=
                   '*Text, Text.\n'
                   ,justify=LEFT, wraplength=800)
    label2.place(rely=.91, relx=.5, anchor=CENTER)
    
    

    ## Buttons
    button1 = Button(frame_main, text='Import File', command=lambda: import_file_page())
    button1.place(rely=0.35, relx=.40, x=-5, width=80, anchor=CENTER)

    button2 = Button(frame_main, text='Paste Data', command=lambda: paste_data_page())
    button2.place(rely=0.35, relx=0.60, x=5, width=80, anchor=CENTER)

    button3 = Button(frame_main, text='Remove List of Wafers', command=lambda: remove_wafers_page())
    button3.place(rely=0.50, relx=0.50, width=165, anchor=CENTER)

    button4 = Button(frame_main, text='Combine EWRs', command=lambda: merge_ewr_page())
    button4.place(rely=0.65, relx=0.50, width=90, anchor=CENTER)

## Main Menu Page End


## About Page Start

def about_page():
    for widget in root.winfo_children():
        widget.destroy()
    
    main_btn()
    about_btn()
    
    page_title = Label(root, text='About EWR Builder')
    page_title.place(relx=.5, y=37, anchor=CENTER)
    page_title.config(font=('arial', 20))

    frame_support = LabelFrame(root, text='Support', font=18, bd=2, relief='ridge')
    frame_support.place(height=130, width=625, rely=0.5, relx=.5, y=-175, anchor=CENTER)

    frame_about = LabelFrame(root, text='About EWR', font=18, bd=2, relief='ridge')
    frame_about.place(height=400, width=625, rely=0.5, relx=.5, y=115, anchor=CENTER)

    canvas_about = Canvas(frame_about)
    canvas_about.pack(side=LEFT, fill=BOTH, padx=5, pady=5, expand=1)
    
    canvas_scrollbar = ttk.Scrollbar(frame_about, orient=VERTICAL, command=canvas_about.yview)
    canvas_scrollbar.pack(side=RIGHT, fill=Y)
    canvas_about.config(yscrollcommand=canvas_scrollbar.set)
    canvas_about.bind('<Configure>', lambda e: canvas_about.configure(scrollregion=canvas_about.bbox('all')))

    canvas_text = Frame(canvas_about)
    canvas_about.create_window((0,0),window=canvas_text, anchor=NW)

    msg_support = Label(frame_support, text=
            'Hello User, thank you for using EWR Builder and we hope it has been '
            'useful to you. EWR Builder has been built by Intern, Louis Cundari III and '
            'Project Lead, Justin Zhu. If you need support in any way or suggestions '
            'that may improve this tool`s fuctionality, please contact us by email or '
            'slack.'
            '\n'
            '\nLouis Cundari III: louiscundari@ibm.com'
            '\nJustin Zhu: hai.zhu@ibm.com'
            ,wraplength=615, justify=LEFT)
    msg_support.place(y=5, x=5)

    msg_about = Label(canvas_text, text=
            'Version: EWR Builder ' + version_num +
            '\nRelease Date: ' + release_date +
            '\nCopyright © 2021 IBM Corp. All rights reserved.'
            '\n\nThe Engineering Work Request Builder or EWR Builder, is a tool to automate '
            'the creation of Baldy compatible EWR files from Samsung reference data. '
            'With EWR Builder you can also easily remove a list of wafers or combine '
            '2 EWRs together.'
            '\n\nReference Data Requirements:'
            '\n-Must be either a .csv or .xlsx file, or some pasted data deliminated by '
            'commas or tabs'
            '\n-Must contain 1 of the following combinations of columns:'
            '\n    1) Wafer ID and Short Desc'
            '\n    2) Lot ID, Wafer Num, and Short Desc'
            '\n    3) Lot ID and Short Desc'
            '\n-Short Desc column must be the LAST column'
            '\n-Extra columns can exist'
            '\n-Headers are not required'
            '\n\nEWR Generation:'
            '\nTo generate an EWR, select Import File or Paste Data. Then click the '
            'Process File button. The EWR is now displayed and a file has been created '
            'in the format, FILENAME_EWR.csv.'
            '\n\nRemove a List of Wafers:'
            '\nTo remove a list of wafers, select Remove List of Wafers. Then, import a '
            'completed EWR. Then enter a valid list of Wafer IDs. Once complete, a new '
            'file will be created in the format, FILENAME_#_wfrs_removed.csv'
            '\nAcceptable lists: complete Baldy error message, or a comma, row, or tab '
            'separated list of Wafer IDs.'
            '\n\nCombine EWRs:'
            '\nTo combine EWRs, import 2 complete EWRs by selecting File 1 and File 2. '
            'Then select a method, Stack or Merge. Enter a new name in the popup and '
            'click OK. The data is now displayed and a new file is saved. To repeat, '
            'select Clear Data.'
            '\nStack: This method usually consists of two different wafer sets that '
            'undergo the same process steps. Stack simply turns the two files into '
            'one file. File 1 will be on top of File 2.'
            '\nMerge: This method usually consists of the same set of wafers and is '
            'used to combine the process steps (short descriptions). The new short '
            'description will look like desc1+desc2. The long description will be a '
            'copy of the short description.'
            '\n\nOption Defaults:'
            '\nIf you would like to change the defaults of the EWR Builder options, '
            'you must edit the source code. Open this file in a text editor and go '
            'to line 38 for more instructions...'
            ,wraplength=590, justify=LEFT)
    msg_about.pack(side=LEFT)


## About Page Start
def stats_page(df):
    try:
        df
    except:
        return
        
    window_summary = Toplevel()
    window_summary.title('EWR Builder - ' + version_num)
    
    window_height = 700
    window_width = 550

    screen_width = window_summary.winfo_screenwidth()
    screen_height = window_summary.winfo_screenheight()

    x_coordinate = int((screen_width/2) - (window_width/2))
    y_coordinate = int((screen_height/2) - (window_height/2))

    window_summary.geometry('{}x{}+{}+{}'.format(window_width, window_height, x_coordinate, y_coordinate))

    window_summary.pack_propagate(False)

    ## Grid Start
    header_frame = LabelFrame(window_summary, bd=1, relief='flat')
    shortdesc_frame = LabelFrame(window_summary, text='Short Descriptions', font=14, relief='ridge')
    droppedrows_frame = LabelFrame(window_summary, text='Rows Missing Data (dropped)', font=14, relief='ridge')
    duprows_frame = LabelFrame(window_summary, text='Duplicate Rows Dropped', font=14, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
    shortdesc_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
    duprows_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
    droppedrows_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
    
    shortdesc_frame.config(font=('arial', 12))
    droppedrows_frame.config(font=('arial', 12))
    duprows_frame.config(font=('arial', 12))

    page_title = Label(header_frame, text='More Data')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 20))

    ## Short Descriptions
    textbox_shortdesc = Text(shortdesc_frame, wrap='none')
    textbox_shortdesc.place(relheight=1, relwidth=1)
    textscrolly = Scrollbar(shortdesc_frame, orient='vertical', command=textbox_shortdesc.yview)
    textscrollx = Scrollbar(shortdesc_frame, orient='horizontal', command=textbox_shortdesc.xview)
    textbox_shortdesc.config(xscrollcommand=textscrollx.set, yscrollcommand=textscrolly.set)
    textscrollx.pack(side='bottom', fill='x')
    textscrolly.pack(side='right', fill='y')

    shortdesc_list = df['SHORTDESC'].unique().tolist()
    shortdesc_list = sorted(shortdesc_list)    
    
    textbox_shortdesc.insert(INSERT, '\n'.join(shortdesc_list))
    textbox_shortdesc.config(state=DISABLED)

    ## Dropped Rows
    nan_rows_calculate(df)   
    textbox_droppedrows = Text(droppedrows_frame, wrap='none')
    textbox_droppedrows.place(relheight=1, relwidth=1)
    textscrolly = Scrollbar(droppedrows_frame, orient='vertical', command=textbox_droppedrows.yview)
    textscrollx = Scrollbar(droppedrows_frame, orient='horizontal', command=textbox_droppedrows.xview)
    textbox_droppedrows.config(xscrollcommand=textscrollx.set, yscrollcommand=textscrolly.set)
    textscrollx.pack(side='bottom', fill='x')
    textscrolly.pack(side='right', fill='y')

    if 'Empty DataFrame' in DF_NAN_ROWS:
        textbox_droppedrows.insert(INSERT, 'None')
        textbox_droppedrows.config(state=DISABLED)
    else:
        textbox_droppedrows.insert(INSERT, DF_NAN_ROWS)
        textbox_droppedrows.config(state=DISABLED)

    ## Duplicate Rows
    textbox_duprows = Text(duprows_frame, wrap='none')
    textbox_duprows.place(relheight=1, relwidth=1)
    textscrolly = Scrollbar(duprows_frame, orient='vertical', command=textbox_duprows.yview)
    textscrollx = Scrollbar(duprows_frame, orient='horizontal', command=textbox_duprows.xview)
    textbox_duprows.config(xscrollcommand=textscrollx.set, yscrollcommand=textscrolly.set)
    textscrollx.pack(side='bottom', fill='x')
    textscrolly.pack(side='right', fill='y')
    
    if DF_DUP_ROWS.empty:
        textbox_duprows.insert(INSERT, 'None')
        textbox_duprows.config(state=DISABLED)
    else:
        textbox_duprows.insert(INSERT, DF_DUP_ROWS)
        textbox_duprows.config(state=DISABLED)
        
    ## Grid configuration
    window_summary.grid_rowconfigure(0, weight=1)
    window_summary.grid_rowconfigure(1, weight=3)
    window_summary.grid_rowconfigure(2, weight=2)
    window_summary.grid_rowconfigure(3, weight=2)

    window_summary.grid_columnconfigure(0, weight=2)
    window_summary.grid_columnconfigure(1, weight=2)


## Import File Page Start
def import_file_page():
    global FILEPATH_LABEL
    global TREE_EWR_DATA
    global STAT1_LABEL ## ** Statistic Var
    global STAT2_LABEL ## ** Statistic Var
    global STAT3_LABEL ## ** Statistic Var
    global STAT4_LABEL ## ** Statistic Var
    global STAT5_LABEL ## ** Statistic Var
    
    for widget in root.winfo_children():
        widget.destroy()
    
    ## Grid Start
    header_frame = LabelFrame(root, bd=1, relief='flat')
    treeview_frame = LabelFrame(root, text='EWR Data', font=18, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=18, bd=2, relief='ridge')
    summary_frame = LabelFrame(root, text='Summary', font=18, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    treeview_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=2, column=0, sticky='nsew', padx=2, pady=2)
    summary_frame.grid(row=2, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
    ## Grid End
    
    main_btn()
    
    page_title = Label(header_frame, text='EWR Builder: Import a File')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 20))
    
    ## Treeview widget
    TREE_EWR_DATA = ttk.Treeview(treeview_frame)
    TREE_EWR_DATA.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(TREE_EWR_DATA, orient='vertical', command=TREE_EWR_DATA.yview)
    treescrollx = Scrollbar(TREE_EWR_DATA, orient='horizontal', command=TREE_EWR_DATA.xview)
    TREE_EWR_DATA.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')    
    
    ## Buttons
    button1 = Button(button_frame, text='Import File', command=lambda: file_select_ewrcreate(TREE_EWR_DATA))
    button1.place(y=30, relx=.5, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Process Data', command=lambda: process_file())
    button2.place(y=70, relx=.5, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Clear Data', command=lambda: clear_data())
    button3.place(y=110, relx=.5, width=80, anchor=CENTER)
    
    checkbox_por = Checkbutton(button_frame, text='Force POR as CellNo 0', 
                            variable=checkbox_por_state, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_por.place(y=140, relx=.5, anchor=CENTER)

    checkbox_truncate = Checkbutton(button_frame, text='Shorten description to 16 char limit', 
                            variable=checkbox_truncate_state, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_truncate.place(y=162, relx=.5, anchor=CENTER)

    checkbox_sort = Checkbutton(button_frame, text='Sort wafer IDs alphanumerically', 
                            variable=checkbox_sort_state, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_sort.place(y=184, relx=.5, anchor=CENTER)
    
    optionmenu_lable = Label(button_frame, text='Select letter casing for descriptions:', wraplength=500, justify=LEFT)
    optionmenu_lable.place(y=205, relx=.5, anchor=CENTER)

    case_options = ['Lower case', 'Upper case', 'Preserve case (long desc. only)']
    option_letter_case.set(case_options[0])
    optionmenu_format1 = OptionMenu(button_frame, option_letter_case, *case_options)
    optionmenu_format1.place(y=230, relx=.5, anchor=CENTER)
    
    
    ## Statistics
    FILEPATH_LABEL = Label(summary_frame, text='File Location: ', wraplength=450, justify=LEFT)
    FILEPATH_LABEL.place(y=10, x=10)

    STAT1_LABEL = Label(summary_frame, text='Total Lot ID5s: ', wraplength=350, justify=LEFT)
    STAT1_LABEL.place(y=55, x=10)

    STAT2_LABEL = Label(summary_frame, text='Total Wafer IDs: ', wraplength=350, justify=LEFT)
    STAT2_LABEL.place(y=75, x=10)

    STAT3_LABEL = Label(summary_frame, text='Total Cells: ', wraplength=350, justify=LEFT)
    STAT3_LABEL.place(y=95, x=10)

    STAT4_LABEL = Label(summary_frame, text='Duplicate Wafer IDs (last ID kept): ', wraplength=350, justify=LEFT)
    STAT4_LABEL.place(y=115, x=10)
    
    STAT5_LABEL = Label(summary_frame, text='Rows missing data (dropped): ', wraplength=350, justify=LEFT)
    STAT5_LABEL.place(y=135, x=10)
    
    button4 = Button(summary_frame, text='More data', command=lambda: stats_page(DF_EWR))
    button4.place(y=160, x=10, width=80)

    
    ## Grid configuration
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=5)
    root.grid_rowconfigure(2, weight=4)

    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=3)

def file_select_ewrcreate(file_data):
    global FILEPATH
    
    try:
        FILEPATH = file_select_window(TREE_EWR_DATA)
        if FILEPATH == '' or FILEPATH is None:
            return None
        FILEPATH_LABEL['text'] = 'File Location: ' + FILEPATH ## text property of label_file is the filename 
        return FILEPATH
    except:
        return

def process_file():
    if FILEPATH is None:
        return
    if os.path.exists(FILEPATH) is True:
        print(FILEPATH)
    else:
        return
    if len(DF_INPUT.columns) < 2:
        messagebox.showerror('EWR Builder', 'File failed. Only 1 column was found.')
        return
    # try:
    ewr_create(FILEPATH, t_f_import=True)
    # except:
    #     messagebox.showerror('EWR Builder', 'File failed.')
    #     return
    ##** this block could be optimized as a function and df/df_new would be the input ## block is used to create static page for Inport File and Paste Data...would probably create more global vars
    print('Dataframe columns:')
    print(DF_EWR.columns.values)
    TREE_EWR_DATA['columns'] = list(DF_EWR.columns) # ex) data['attribute']
    TREE_EWR_DATA['show'] = 'headings'
    for column in TREE_EWR_DATA['columns']:
        TREE_EWR_DATA.heading(column, text=column)
    df_rows = DF_EWR.to_numpy().tolist()
    for row in df_rows: # for each row in df, insert into tree view
        TREE_EWR_DATA.insert('', 'end', values=row)
    FILEPATH_LABEL['text'] = 'File Location: ' + EWR_filepath
    TREE_EWR_DATA.column('#LOTID', width=90, stretch=NO)
    TREE_EWR_DATA.column('WAFERID', width=90, stretch=NO)
    TREE_EWR_DATA.column('CELLNO', width=75, stretch=NO)
    TREE_EWR_DATA.column('SHORTDESC', width=110, stretch=YES)
    TREE_EWR_DATA.column('LONGDESC', width=110, stretch=YES)

    stats_general()
    
    print('Completed EWR:')
    print(DF_EWR)

def clear_data():
    global filepath
    try:
        TREE_EWR_DATA.delete(*TREE_EWR_DATA.get_children()) #unpack all rows
        TREE_EWR_DATA['columns'] = list(DF_INPUT.columns)
        FILEPATH_LABEL['text'] = 'File Location: '
        filepath = None
        
        STAT1_LABEL['text'] = 'Total Lot ID5s: '
        STAT2_LABEL['text'] = 'Total Wafer IDs: '
        STAT3_LABEL['text'] = 'Total Cells: '
        STAT4_LABEL['text'] = 'Duplicate Wafer IDs (last ID kept): '
        STAT5_LABEL['text'] = 'Rows missing data (dropped): '
        
    except: 
        return


## Import File Page End


# Paste Data Page Start

def paste_data_page():
    global TEXTBOX_PASTE
    global textbox_treeview_frame
    global FILEPATH_LABEL
    global STAT1_LABEL
    global STAT2_LABEL
    global STAT3_LABEL
    global STAT4_LABEL
    global STAT5_LABEL
    
    for widget in root.winfo_children():
        widget.destroy()
    
    ## Grid Start
    header_frame = LabelFrame(root, bd=1, relief='flat')
    textbox_treeview_frame = LabelFrame(root, text='Enter EWR Data', font=18, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=18, bd=2, relief='ridge')
    summary_frame = LabelFrame(root, text='Summary', font=18, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    textbox_treeview_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=2, column=0, sticky='nsew', padx=2, pady=2)
    summary_frame.grid(row=2, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
    ## Grid End
    
    main_btn()
    
    page_title = Label(header_frame, text='EWR Builder: Paste Data')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 20))
    
    ## Textbox widget
    TEXTBOX_PASTE = Text(textbox_treeview_frame, undo=True)
    TEXTBOX_PASTE.place(relheight=1, relwidth=1)
    textscrolly = Scrollbar(textbox_treeview_frame, orient='vertical', command=TEXTBOX_PASTE.yview)
    textscrollx = Scrollbar(textbox_treeview_frame, orient='horizontal', command=TEXTBOX_PASTE.xview)
    TEXTBOX_PASTE.config(xscrollcommand=textscrollx.set, yscrollcommand=textscrolly.set)
    textscrollx.pack(side='bottom', fill='x')
    textscrolly.pack(side='right', fill='y')

    ## Buttons
    button1 = Button(button_frame, text='Process Data', command=lambda: export_temp())
    button1.place(y=30, relx=.5, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Clear Data', command=lambda: clear_text())
    button2.place(y=70, relx=.5, width=80, anchor=CENTER)
    
    checkbox_por = Checkbutton(button_frame, text='Force POR as CellNo 0',
                        variable=checkbox_por_state, onvalue=1, offvalue=0, height=1, justify=LEFT)
    checkbox_por.place(y=100, relx=.5, anchor=CENTER)

    checkbox_truncate = Checkbutton(button_frame, text='Shorten description to 16 char limit', 
                            variable=checkbox_truncate_state, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_truncate.place(y=122, relx=.5, anchor=CENTER)
    
    checkbox_sort = Checkbutton(button_frame, text='Sort wafer IDs alphanumerically', 
                            variable=checkbox_sort_state, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_sort.place(y=144, relx=.5, anchor=CENTER)
    
    optionmenu_lable = Label(button_frame, text='Select letter casing for descriptions:', wraplength=500, justify=LEFT)
    optionmenu_lable.place(y=165, relx=.5, anchor=CENTER)

    case_options = ['Lower case', 'Upper case', 'Preserve case (long desc. only)']
    option_letter_case.set(case_options[0])
    optionmenu_format1 = OptionMenu(button_frame, option_letter_case, *case_options)
    optionmenu_format1.place(y=190, relx=.5, anchor=CENTER)

    ## Statistics
    FILEPATH_LABEL = Label(summary_frame, text='File Location: ', wraplength=450, justify=LEFT)
    FILEPATH_LABEL.place(y=10, x=10)

    STAT1_LABEL = Label(summary_frame, text='Total Lot ID5s: ', wraplength=350, justify=LEFT)
    STAT1_LABEL.place(y=60, x=10)

    STAT2_LABEL = Label(summary_frame, text='Total Wafer IDs: ', wraplength=350, justify=LEFT)
    STAT2_LABEL.place(y=80, x=10)

    STAT3_LABEL = Label(summary_frame, text='Total Cells: ', wraplength=350, justify=LEFT)
    STAT3_LABEL.place(y=100, x=10)

    STAT4_LABEL = Label(summary_frame, text='Duplicate Wafer IDs (last ID kept): ', wraplength=350, justify=LEFT)
    STAT4_LABEL.place(y=120, x=10)
    
    STAT5_LABEL = Label(summary_frame, text='Rows missing data (dropped): ', wraplength=350, justify=LEFT)
    STAT5_LABEL.place(y=140, x=10)

    button4 = Button(summary_frame, text='More data', command=lambda: stats_page(DF_EWR))
    button4.place(y=160, x=10, width=80)

    # Grid Configuration
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=5)
    root.grid_rowconfigure(2, weight=4)

    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=3)

    
def clear_text():
    for widget in textbox_treeview_frame.winfo_children():
        widget.destroy()
    paste_data_page()
    
def export_temp():
    if len(TEXTBOX_PASTE.get('1.0', 'end-1c')) == 0:
        return
    
    temp_file = open(path_temp, 'w')
    temp_file.write(TEXTBOX_PASTE.get('1.0', 'end'))
    temp_file.close()
    
    pastedata_path = simpledialog.askstring('EWR Builder', 'Enter a file name (do not add file extension):', parent=root).strip()
    while os.path.exists(pastedata_path + '_EWR.csv') is True or pastedata_path == '':
        pastedata_path = simpledialog.askstring('EWR Builder', 'File already exists. Enter a new file name (do not add file extension):', parent=root).strip() 

    if pastedata_path == '' or pastedata_path is None:
        remove_temp(path_temp)
        return None
    print('Pasted data path: ')
    print(pastedata_path)
    
    # try:
    if pastedata_path is not None or pastedata_path != '':
        os.rename(path_temp, pastedata_path)
        process_text(pastedata_path)
    #     else:
    #         remove_temp(path_temp)
    #         return None
    # except:
    #     remove_temp(path_temp)

def process_text(filepath): ## F24
    global DF_INPUT

    try:
        DF_INPUT = pd.read_csv(filepath, sep=',', dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
        if len(DF_INPUT.columns) < 2:
            raise ValueError('Incorrect delimiter.')
        else:
            ewr_create(filepath, t_f_import=False)
        
    except ValueError:
        DF_INPUT = pd.read_csv(filepath, sep='\t', dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
        if len(DF_INPUT.columns) < 2:
            raise ValueError('Incorrect delimiter.')
        else:
            ewr_create(filepath, t_f_import=False)

    except:
        if filepath is None:
            return
        messagebox.showerror('EWR Builder', 'File failed.')
        remove_temp(filepath)
        return None
    
    remove_temp(filepath)
    TEXTBOX_PASTE.destroy()

    TREE_PASTE_DATA = ttk.Treeview(textbox_treeview_frame)
    TREE_PASTE_DATA.place(relheight=1, relwidth=1)

    TREE_PASTE_DATA.delete(*TREE_PASTE_DATA.get_children()) #unpack all rows
    
    TREE_PASTE_DATA['columns'] = list(DF_EWR.columns) # ex) data['attribute']
    TREE_PASTE_DATA['show'] = 'headings'
    for column in TREE_PASTE_DATA['columns']:
        TREE_PASTE_DATA.heading(column, text=column)
    df_rows = DF_EWR.to_numpy().tolist()
    for row in df_rows: # for each row in df, insert into tree view
        TREE_PASTE_DATA.insert('', 'end', values=row)
    FILEPATH_LABEL['text'] = 'File Location: ' + EWR_filepath
    TREE_PASTE_DATA.column('#LOTID', width=90, stretch=NO)
    TREE_PASTE_DATA.column('WAFERID', width=90, stretch=NO)
    TREE_PASTE_DATA.column('CELLNO', width=75, stretch=NO)
    TREE_PASTE_DATA.column('SHORTDESC', width=110, stretch=YES)
    TREE_PASTE_DATA.column('LONGDESC', width=110, stretch=YES)

    treescrolly = Scrollbar(TREE_PASTE_DATA, orient='vertical', command=TREE_PASTE_DATA.yview)
    treescrollx = Scrollbar(TREE_PASTE_DATA, orient='horizontal', command=TREE_PASTE_DATA.xview)
    TREE_PASTE_DATA.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')
    
    stats_general()
    

# Paste Data Page End


## Remove-List-of-Wafers Page Start

def remove_wafers_page():
    global text_frame
    global TEXTBOX_REMOVAL
    global FILEPATH_LABEL
    global STAT1_LABEL
    global STAT2_LABEL
    global STAT3_LABEL
    global STAT4_LABEL
    global STAT5_LABEL
    
    for widget in root.winfo_children():
        widget.destroy()
    
    ## Grid Start
    header_frame = LabelFrame(root, bd=1, relief='flat')
    text_frame = LabelFrame(root, text='Wafer List', font=18, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=18, bd=2, relief='ridge')
    summary_frame = LabelFrame(root, text='Summary', font=18, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    text_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=2, column=0, sticky='nsew', padx=2, pady=2)
    summary_frame.grid(row=2, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
    ## Grid End
    
    main_btn()
    
    page_title = Label(header_frame, text='EWR Builder: Remove List of Wafers')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 20))
    
    ## Textbox widget
    TEXTBOX_REMOVAL = Text(text_frame, undo=True)
    TEXTBOX_REMOVAL.place(relheight=1, relwidth=1)
    textscrolly = Scrollbar(text_frame, orient='vertical', command=TEXTBOX_REMOVAL.yview)
    textscrollx = Scrollbar(text_frame, orient='horizontal', command=TEXTBOX_REMOVAL.xview)
    TEXTBOX_REMOVAL.config(xscrollcommand=textscrollx.set, yscrollcommand=textscrolly.set)
    textscrollx.pack(side='bottom', fill='x')
    textscrolly.pack(side='right', fill='y')
    
    ## Buttons
    button1 = Button(button_frame, text='Import File', command=lambda: remove_wafers_file_dialog())
    button1.place(y=50, relx=.5, width=90, anchor=CENTER)
    
    button2 = Button(button_frame, text='Remove Wafers', command=lambda: remove_wafers_confirm())
    button2.place(y=90, relx=.5, width=90, anchor=CENTER)
    
    button3 = Button(button_frame, text='Clear Data', command=lambda: clear_text_remove_wafers(t_f_import_rmv=False))
    button3.place(y=130, relx=.5, width=90, anchor=CENTER)
    
    ## Statistics
    FILEPATH_LABEL = Label(summary_frame, text='File Location: ', wraplength=450, justify=LEFT)
    FILEPATH_LABEL.place(y=10, x=10)

    STAT1_LABEL = Label(summary_frame, text='Total Lot ID5s: ', wraplength=350, justify=LEFT)
    STAT1_LABEL.place(y=60, x=10)

    STAT2_LABEL = Label(summary_frame, text='Total Wafer IDs: ', wraplength=350, justify=LEFT)
    STAT2_LABEL.place(y=80, x=10)

    STAT3_LABEL = Label(summary_frame, text='Total Cells: ', wraplength=350, justify=LEFT)
    STAT3_LABEL.place(y=100, x=10)

    STAT4_LABEL = Label(summary_frame, text='Removed Wafer IDs: ', wraplength=350, justify=LEFT)
    STAT4_LABEL.place(y=120, x=10)

    STAT5_LABEL = Label(summary_frame, text='Removed Cells: ', wraplength=350, justify=LEFT)
    STAT5_LABEL.place(y=140, x=10)

    ## Grid configuration
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=5)
    root.grid_rowconfigure(2, weight=4)

    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=3)


def remove_wafers_file_dialog():
    global DF_REMOVAL ##  ** check if needed
    global FILENAME_RMV_WAFERS
    
    FILENAME_RMV_WAFERS = filedialog.askopenfilename(title='Select a File', filetype=(('EWR Files', '*.csv *.xlsx *.txt'),
                                                                                    ('Excel Files', '*.xlsx *.xls *.xlsb *.xlsm'),
                                                                                    ('All Files', '*.*')))
    if FILENAME_RMV_WAFERS == '' or FILENAME_RMV_WAFERS is None:
        return None
    clear_text_remove_wafers(t_f_import_rmv=True)
    FILEPATH_LABEL['text'] = 'File Location: ' + FILENAME_RMV_WAFERS ## text property of label_file is the filename 
    try:
        DF_REMOVAL = pd.read_csv(FILENAME_RMV_WAFERS, dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
        print(DF_REMOVAL)
    except:
        print('No file selected.')
        return None
    return None

def delimiter_automation(delimiter): ## to simplify the delimiter if-block ** not used yet
    remove_wafers_text = TEXTBOX_REMOVAL.get('1.0', 'end').replace(' ', '')
    remove_wafers_text = remove_wafers_text.strip()
    remove_wafers_list = [str(waferid) for waferid in remove_wafers_text.split(delimiter)]
    if '' in remove_wafers_list:
        remove_wafers_list = list(filter(None, remove_wafers_list))
    print('Wafers to be removed:')
    print(remove_wafers_list)
    return remove_wafers_list
    
def remove_wafers_confirm():
    global DF_REMOVAL ## remove_wafers_confirm and remove_wafers_file_dialog
    global FILENAME_RMV_WAFERS
    
    if FILENAME_RMV_WAFERS == '' or FILENAME_RMV_WAFERS is None:
        return None
    
    remove_wafers_text = TEXTBOX_REMOVAL.get('1.0', 'end').replace(' ', '')
    remove_wafers_text = remove_wafers_text.strip()
    # print(remove_wafers_text)
    if len(remove_wafers_text) == 0:
        return None
    remove_wafers_text = remove_wafers_text.strip()
    # print(remove_wafers_text)
    try:
        try:
            temp_file = open(path_temp, 'w')
            temp_file.write(TEXTBOX_REMOVAL.get('1.0', 'end'))
            temp_file.close()
            
            df_baldy = pd.read_csv(path_temp, dtype=str, skip_blank_lines=True, header=None) #.dropna().reset_index(drop=True)
            wafers_to_rmv = []
            for row in df_baldy[0]:
                # print(row)
                wafer = re.findall("'([^']*)'", row) ## checks for wafer id inside single quotes
                wafers_to_rmv.append(wafer[1])
                # print(wafer[1])
            # print(wafers_to_rmv)
            remove_wafers_list = wafers_to_rmv
            # print(remove_wafers_list)
            # return
            # remove_temp(path_temp)
            
            print('Baldy Output wafer list.')

        except:
            remove_temp(path_temp)
            
            remove_wafers_text = TEXTBOX_REMOVAL.get('1.0', 'end').replace(' ', '').strip()
            remove_wafers_list = [str(waferid) for waferid in remove_wafers_text.split('\n')]
            if '' in remove_wafers_list:
                remove_wafers_list = list(filter(None, remove_wafers_list))
            # print(remove_wafers_list)
            if len(remove_wafers_list) == 1:
                remove_wafers_text = TEXTBOX_REMOVAL.get('1.0', 'end').replace(' ', '').strip()
                remove_wafers_list = [str(waferid) for waferid in remove_wafers_text.split(',')]
                if '' in remove_wafers_list:
                    remove_wafers_list = list(filter(None, remove_wafers_list))
                # print(remove_wafers_list)
                if len(remove_wafers_list) == 1:
                    remove_wafers_text = TEXTBOX_REMOVAL.get('1.0', 'end').replace(' ', '').strip()
                    remove_wafers_list = [str(waferid) for waferid in remove_wafers_text.split('\t')]
                    if '' in remove_wafers_list:
                        remove_wafers_list = list(filter(None, remove_wafers_list))
                    # print(remove_wafers_list)
                    if len(remove_wafers_list) == 1:
                        remove_wafers_list = [str(waferid) for waferid in remove_wafers_text.split()]     
                    else:
                        print('Tab-separated wafers:')
                        print(remove_wafers_list)
                else:
                    print('Comma-separated wafers:')
                    print(remove_wafers_list)                
            else:
                print('Row-separated wafers:')
                print(remove_wafers_list)

        
        remove_y_n = messagebox.askyesno('Confirm Removal', 'Remove these Wafer IDs?:\n' + ', '.join(remove_wafers_list))
        if remove_y_n is True:

            num_cellno_initial = len(DF_REMOVAL['SHORTDESC'].unique())
            df_length_initial = len(DF_REMOVAL)
            DF_REMOVAL['SHORTDESC'] = DF_REMOVAL['SHORTDESC'].str.casefold()
            df_removal_new = DF_REMOVAL[~DF_REMOVAL['WAFERID'].isin(remove_wafers_list)].reset_index(drop=True) ## ** 'isin' is case sensitive... shouldnt be a problem since all wafers are uppercase
            df_length_final = len(df_removal_new)
            num_rows_removed = df_length_initial - df_length_final
            num_cellno_final = len(df_removal_new['SHORTDESC'].unique())
            num_cellno_removed = num_cellno_initial - num_cellno_final
            
            cellno_assign(df_removal_new, t_f_removal=True)

            removal_filepath = os.path.splitext(FILENAME_RMV_WAFERS)[0] + '_' + str(num_rows_removed) + '_wfrs_removed.csv'
            df_removal_new.to_csv(removal_filepath, index=False)
            messagebox.showinfo('EWR Builder', 'Complete.\n\n' + 'Wafer IDs removed: ' + str(num_rows_removed) + '\nFile saved to: ' + removal_filepath)

            stats_merge(df_removal_new)

            FILEPATH_LABEL['text'] = 'File Location: ' + str(removal_filepath)
            STAT1_LABEL['text'] = 'Total Lot ID5s: ' + NUM_UNIQUE_LOTIDS
            STAT2_LABEL['text'] = 'Total Wafer IDs: ' + NUM_UNIQUE_WAFERIDS
            STAT3_LABEL['text'] = 'Total Cells: ' + str(NUM_TOTAL_CELLS)
            STAT4_LABEL['text'] = 'Removed Wafer IDs: ' + str(num_rows_removed)
            STAT5_LABEL['text'] = 'Removed Cells: ' + str(num_cellno_removed)

            print(str(num_rows_removed) + ' Wafer IDs were removed.')
            
            FILENAME_RMV_WAFERS = ''
        
    except KeyError:
        messagebox.showerror('EWR Builder', 'KeyError.\nEnsure the file contains the correct headers:\n#LOTID, WAFERID, CELLNO, SHORTDESC, LONGDESC')
        return None
    except:
        remove_temp(path_temp)
        messagebox.showerror('EWR Builder', 'File failed.')
        return None

def clear_text_remove_wafers(t_f_import_rmv):
    wafer_removal_text = TEXTBOX_REMOVAL.get('1.0', 'end')
    for widget in text_frame.winfo_children():
        widget.destroy()
    remove_wafers_page()
    
    if t_f_import_rmv is True:
        print(wafer_removal_text)
        TEXTBOX_REMOVAL.insert('1.0', wafer_removal_text)
        
## Remove-List-of-Wafers Page End

## Merge EWRs Page Start

def merge_ewr_page():
    global FILEPATH_LABEL
    global filepath_merge1_label
    global filepath_merge2_label
    global treeview_file1
    global treeview_file2
    global file1_data
    global file2_data
    global STAT1_LABEL
    global STAT2_LABEL
    global STAT3_LABEL
    global STAT4_LABEL
    global STAT5_LABEL 
    
    for widget in root.winfo_children():
        widget.destroy()
    
    ## Grid Start
    header_frame = LabelFrame(root, bd=1, relief='flat')
    treeview_file1 = LabelFrame(root, text='File 1', font=18, bd=2, relief='ridge')
    treeview_file2 = LabelFrame(root, text='File 2', font=18, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=18, bd=2, relief='ridge')
    summary_frame = LabelFrame(root, text='Summary', font=18, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    treeview_file1.grid(row=1, column=0, columnspan=1, sticky='nsew', padx=2, pady=2)
    treeview_file2.grid(row=1, column=1, columnspan=3, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=2, column=0, sticky='nsew', padx=2, pady=2)
    summary_frame.grid(row=2, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
    ## Grid End
    
    main_btn()
    
    page_title = Label(header_frame, text='EWR Builder: Combine EWRs')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 20))
    
    ## Treeview widgets
    file1_data = ttk.Treeview(treeview_file1)
    file1_data.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(file1_data, orient='vertical', command=file1_data.yview)
    treescrollx = Scrollbar(file1_data, orient='horizontal', command=file1_data.xview)
    file1_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')

    file2_data = ttk.Treeview(treeview_file2)
    file2_data.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(file2_data, orient='vertical', command=file2_data.yview)
    treescrollx = Scrollbar(file2_data, orient='horizontal', command=file2_data.xview)
    file2_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')
    
    # ## Buttons
    button1 = Button(button_frame, text='File 1', command=lambda: file_select1(file1_data))
    button1.place(y=50, relx=.50, x=-50, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='File 2', command=lambda: file_select2(file2_data))
    button2.place(y=90, relx=.50, x=-50, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Stack', command=lambda: merge_ewr_stack(FILE1, FILE2))
    button3.place(y=50, relx=.50, x=50, width=80, anchor=CENTER)
    
    button4 = Button(button_frame, text='Merge', command=lambda: merge_ewr_descriptions(FILE1, FILE2))
    button4.place(y=90, relx=.50, x=50, width=80, anchor=CENTER)
    
    button5 = Button(button_frame, text='Clear Data', command=lambda: clear_merge_ewr())
    button5.place(y=130, relx=.50, width=80, anchor=CENTER)
    
    merge_information = Label(button_frame, text='Stack: File 1 will be on top of File 2 ' 
                              'in a new file. Usually consists of two different wafer sets that '
                              'undergo the same process steps.'
                              '\nMerge: Process steps (short descriptions) will be combined. '
                              'Usually consists of the wafer set but different process steps. ' 
                              , 
                              justify=LEFT, wraplength=350)
    merge_information.place(x=10, y=-10, relx=0, rely=1.0, anchor=SW)
    
    ## Statistics
    filepath_merge1_label = Label(summary_frame, text='File 1: ', wraplength=350, justify=LEFT)
    filepath_merge1_label.place(y=10, x=10)
    
    filepath_merge2_label = Label(summary_frame, text='File 2: ', wraplength=350, justify=LEFT)
    filepath_merge2_label.place(y=60, x=10)

    STAT1_LABEL = Label(summary_frame, text='Total Lot ID5s: ', wraplength=350, justify=LEFT)
    STAT1_LABEL.place(y=110, x=10)

    STAT2_LABEL = Label(summary_frame, text='Total Wafer IDs:  ', wraplength=350, justify=LEFT)
    STAT2_LABEL.place(y=130, x=10)

    STAT3_LABEL = Label(summary_frame, text='Total Cells: ', wraplength=350, justify=LEFT)
    STAT3_LABEL.place(y=150, x=10)

    STAT4_LABEL = Label(summary_frame, text='Duplicate Wafer IDs (last ID kept): ', wraplength=350, justify=LEFT)
    STAT4_LABEL.place(y=170, x=10)
    
    STAT5_LABEL = Label(summary_frame, text='Rows missing data (dropped): ', wraplength=350, justify=LEFT)
    STAT5_LABEL.place(y=190, x=10)
    
    ## Grid configuration
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=5)
    root.grid_rowconfigure(2, weight=4)

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)


def show_treeview_merge(filepath_merge):
    global FRAME_MERGE
    global TREE_MERGE_DATA

    FRAME_MERGE = LabelFrame(root, text='Output File: ' + filepath_merge, font=18, bd=2, relief='ridge') #yellow
    FRAME_MERGE.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    TREE_MERGE_DATA = ttk.Treeview(FRAME_MERGE)
    TREE_MERGE_DATA.place(relheight=1, relwidth=1)

    treescrolly = Scrollbar(TREE_MERGE_DATA, orient='vertical', command=TREE_MERGE_DATA.yview)
    treescrollx = Scrollbar(TREE_MERGE_DATA, orient='horizontal', command=TREE_MERGE_DATA.xview)
    TREE_MERGE_DATA.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')

def file_select1(file_data):
    global FILE1
    global filepath_merge1_label
    
    # try:
    FILE1 = file_select_window(file_data)
    # except:
    #     merge_ewr_page()
    #     FILE1 = file_select_window(file_data)
    
    if FILE1 is None or FILE1 == '':
        return
    filepath_merge1_label['text'] = 'File 1: ' + FILE1
    return FILE1

def file_select2(file_data):
    global FILE2
    global filepath_merge2_label
    
    FILE2 = file_select_window(file_data)
    if FILE2 is None or FILE2 == '':
        return
    filepath_merge2_label['text'] = 'File 2: ' + str(FILE2)
    
    return FILE2

def file_select_window(file_data):
    global FILE
    global DF_INPUT
    
    FILE = filedialog.askopenfilename(title='Select a File', filetype=(('EWR Files', '*.csv *.xlsx *.txt'),
                                                                        ('Excel Files', '*.xlsx *.xls *.xlsb *.xlsm'),
                                                                        ('All Files', '*.*')))
    if FILE == '' or FILE is None:
        return
    else:
        file_data.delete(*file_data.get_children()) #unpack all rows

    if os.path.splitext(FILE)[1] == '.csv':
        import_filename = r'{}'.format(FILE)
        DF_INPUT = pd.read_csv(import_filename, sep=',', dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
        if len(DF_INPUT.columns) < 2:
            DF_INPUT = pd.read_csv(import_filename, sep='\t', dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
    elif os.path.splitext(FILE)[1] == '.xlsx':
        import_filename = r'{}'.format(FILE)
        DF_INPUT = pd.read_excel(import_filename, dtype=str)
        print(DF_INPUT)
    elif os.path.splitext(FILE)[1] == '.txt':
        import_filename = r'{}'.format(FILE)
        DF_INPUT = pd.read_csv(import_filename, sep='\t', dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
        if len(DF_INPUT.columns) < 2:
                DF_INPUT = pd.read_csv(import_filename, sep=',', dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
    else: ## backup
        try:
            import_filename = r'{}'.format(FILE)
            DF_INPUT = pd.read_excel(import_filename, dtype=str)
        except ValueError:
            import_filename = r'{}'.format(FILE)
            DF_INPUT = pd.read_csv(import_filename, sep='\t', dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
        except ValueError:
            import_filename = r'{}'.format(FILE)
            DF_INPUT = pd.read_fwf(import_filename, dtype=str, skip_blank_lines=True, header='infer').reset_index(drop=True)
        except:
            messagebox.showerror('Error', 'This file type/format is not compatable.')
            return None

    ## Code to display dataframe in tree-view
    file_data['columns'] = list(DF_INPUT.columns) # ex) data['attribute']
    file_data['show'] = 'headings'
    for column in file_data['columns']:
        file_data.heading(column, text=column)
    df_rows = DF_INPUT.to_numpy().tolist()
    for row in df_rows: # for each row in df, insert into tree view
        file_data.insert('', 'end', values=row)

    list_headers = DF_INPUT.columns.values.tolist()
    for column in list_headers:
        file_data.column(column, width=10, stretch=YES)
        
    return FILE


def merge_ewr_stack(merge_file1, merge_file2):
    global ewr_merge
    global NUM_DUP_WAFERIDS
    global NUM_NA_ROWS_TOTAL
    if merge_file1 == '' or merge_file1 is None:
        return
    if merge_file2 == '' or merge_file2 is None:
        return
    
    ewr_merge_path = simpledialog.askstring('EWR Builder', 'Enter a file name (do not add file extension):', parent=root).strip()
    while os.path.exists(ewr_merge_path + '.csv') is True or ewr_merge_path == '':
        ewr_merge_path = simpledialog.askstring('EWR Builder', 'File already exists. Enter a new file name (do not add file extension):', parent=root).strip() 

    if ewr_merge_path == '' or ewr_merge_path is None:
        remove_temp(path_temp)
        return None
       
    if ewr_merge_path == '' or ewr_merge_path is None: ## ** maybe replace this with a while loop. If result is '', repeat, if cancel, return
        messagebox.showwarning('EWR Builder', 'Error.\n\n' + 'The file was not saved. No file name was entered.')
        return None
    else:
        ewr_merge_path = path_script + ewr_merge_path.strip() + '.csv'
    
    print('Output file: ' + ewr_merge_path)
    
    df_merge1 = pd.read_csv(merge_file1, dtype=str)
    df_merge2 = pd.read_csv(merge_file2, dtype=str)

    remove_whitespace(df_merge1)
    remove_whitespace(df_merge2)
    df_merge1['LONGDESC'] = df_merge1['LONGDESC'].replace(r'^\s*$', np.nan, regex=True) ## ** function?
    df_merge1['LONGDESC'] = df_merge1['LONGDESC'].str.strip()
    df_merge1['LONGDESC'] = df_merge1['LONGDESC'].fillna(value='uncertain')
    
    df_merge2['LONGDESC'] = df_merge2['LONGDESC'].replace(r'^\s*$', np.nan, regex=True)
    df_merge2['LONGDESC'] = df_merge2['LONGDESC'].str.strip()
    df_merge2['LONGDESC'] = df_merge2['LONGDESC'].fillna(value='uncertain')
    
    ewr_merge = pd.concat([df_merge1, df_merge2], ignore_index=True, sort=False)
    
    na_rows_inital = len(ewr_merge)
    ewr_merge = ewr_merge.dropna().reset_index(drop=True)
    na_rows_final = len(ewr_merge)
    NUM_NA_ROWS_TOTAL =  na_rows_inital - na_rows_final
    NUM_NA_ROWS_TOTAL = str(NUM_NA_ROWS_TOTAL)
    
    dup_waferids_initial = len(ewr_merge)
    ewr_merge.drop_duplicates(keep='last', ignore_index=True)
    ewr_merge.drop_duplicates(subset=['WAFERID'], keep='last', inplace=True)
    dup_waferids_final = len(ewr_merge)
    NUM_DUP_WAFERIDS = dup_waferids_initial - dup_waferids_final
    NUM_DUP_WAFERIDS = str(NUM_DUP_WAFERIDS)
    
    ewr_merge.reset_index(drop=True)
    
    cellno_assign(ewr_merge, t_f_removal=False)
    ewr_merge['#LOTID'] = ewr_merge['#LOTID'].apply(lambda row: row[0:5]) ## F09 
    ewr_merge['#LOTID'] = ewr_merge['#LOTID'].apply(lambda row: row + '.1')
    
    shortdesc_error_list = []
    for shortdesc in ewr_merge['SHORTDESC']:
        if len(shortdesc) > 16:
            shortdesc_error_list.append(shortdesc)
            
    cellno_assign(ewr_merge, t_f_removal=False)

    if len(shortdesc_error_list) > 0:
        messagebox.showwarning('EWR Builder', str(len(shortdesc_error_list)) + ' description(s) are longer than 16 chars. Shorten these descriptions and rerun.\n\n' + '\n'.join(shortdesc_error_list))
        return None
    
    treeview_file1.destroy()
    treeview_file2.destroy()

    show_treeview_merge(ewr_merge_path)

    TREE_MERGE_DATA['columns'] = list(ewr_merge.columns) # ex) data['attribute']
    TREE_MERGE_DATA['show'] = 'headings'
    for column in TREE_MERGE_DATA['columns']:
        TREE_MERGE_DATA.heading(column, text=column)
    ewr_rows = ewr_merge.to_numpy().tolist()
    for row in ewr_rows: # for each row in df, insert into tree view
        TREE_MERGE_DATA.insert('', 'end', values=row)

    TREE_MERGE_DATA.column('#LOTID', width=10, stretch=YES)
    TREE_MERGE_DATA.column('WAFERID', width=10, stretch=YES)
    TREE_MERGE_DATA.column('CELLNO', width=10, stretch=YES)
    TREE_MERGE_DATA.column('SHORTDESC', width=10, stretch=YES)
    TREE_MERGE_DATA.column('LONGDESC', width=10, stretch=YES)
    
    print('Stacked EWR:')
    print(ewr_merge)

    stats_merge(ewr_merge)
    stats_general()
    
    ewr_merge.to_csv(ewr_merge_path, index=False)
    messagebox.showinfo('EWR Builder', 'Complete.\n\n' + 'The file has been saved to: \r' + ewr_merge_path)

    global FILE1 ## ** to be moved into the clear function 
    global FILE2
    FILE1 = None
    FILE2 = None

def merge_ewr_descriptions(merge_file1, merge_file2):
    global ewr_merge
    global NUM_DUP_WAFERIDS
    global NUM_NA_ROWS_TOTAL
    
    if merge_file1 == '' or merge_file1 is None:
        return
    if merge_file2 == '' or merge_file2 is None:
        return
    
    ## ** This block can be optimized Start
    ewr_merge_path = simpledialog.askstring('EWR Builder', 'Enter a file name (do not add file extension):', parent=root).strip()
    while os.path.exists(ewr_merge_path + '.csv') is True or ewr_merge_path == '':
        ewr_merge_path = simpledialog.askstring('EWR Builder', 'File already exists. Enter a new file name (do not add file extension):', parent=root).strip() 

    if ewr_merge_path == '' or ewr_merge_path is None:
        remove_temp(path_temp)
        return None
   
    if ewr_merge_path == '' or ewr_merge_path is None:
        messagebox.showwarning('EWR Builder', 'Error.\n\n' + 'The file was not saved. No file name was entered.')
        return None
    else:
        ewr_merge_path = path_script + ewr_merge_path.strip() + '.csv'
        
    print('Output file: ' + ewr_merge_path)
    
    df_merge1 = pd.read_csv(merge_file1, dtype=str)
    df_merge2 = pd.read_csv(merge_file2, dtype=str)

    ## block removes whitespace from all cells; spaces are kept
    remove_whitespace(df_merge1)
    remove_whitespace(df_merge2)

    df_merge = pd.merge(df_merge1, df_merge2, on=['WAFERID'], how='outer', suffixes=('_df_merge1', '_df_merge2')) ## optimal
    
    df_merge['SHORTDESC_df_merge1'] = df_merge['SHORTDESC_df_merge1'].fillna(value='uncertain')
    df_merge['SHORTDESC_df_merge2'] = df_merge['SHORTDESC_df_merge2'].fillna(value='uncertain')
    
    df_merge['SHORTDESC_df_merge1'] = df_merge['SHORTDESC_df_merge1'].str.replace('uncertain','uncert')
    df_merge['SHORTDESC_df_merge2'] = df_merge['SHORTDESC_df_merge2'].str.replace('uncertain','uncert')
    df_merge.fillna(value={'SHORTDESC_df_merge1': 'uncert', 'SHORTDESC_df_merge2': 'uncert'})

    ewr_merge = df_merge[['WAFERID']].astype(str)
    
    ewr_merge['#LOTID'] = ewr_merge['WAFERID'].apply(lambda row: row[0:5] + '.1')
    ewr_merge['#LOTID'] = ewr_merge['#LOTID'].str.upper()
    
    ewr_merge['CELLNO'] = ''
    ewr_merge['SHORTDESC'] = df_merge['SHORTDESC_df_merge1'].astype(str) + '+' + df_merge['SHORTDESC_df_merge2'].astype(str)
    ewr_merge['LONGDESC'] = ewr_merge['SHORTDESC']

    na_rows_inital = len(ewr_merge)
    ewr_merge = ewr_merge.dropna().reset_index(drop=True)
    na_rows_final = len(ewr_merge)
    NUM_NA_ROWS_TOTAL =  na_rows_inital - na_rows_final
    NUM_NA_ROWS_TOTAL = str(NUM_NA_ROWS_TOTAL)
    
    dup_waferids_initial = len(ewr_merge)
    ewr_merge.drop_duplicates(keep='last', ignore_index=True)
    ewr_merge.drop_duplicates(subset=['WAFERID'], keep='last', inplace=True)
    dup_waferids_final = len(ewr_merge)
    NUM_DUP_WAFERIDS = dup_waferids_initial - dup_waferids_final
    NUM_DUP_WAFERIDS = str(NUM_DUP_WAFERIDS)
    ewr_merge.reset_index(drop=True)
    
    cellno_assign(ewr_merge, t_f_removal=False)

    shortdesc_error_list = []
    for shortdesc in ewr_merge['SHORTDESC']:
        if len(shortdesc) > 16:
            shortdesc_error_list.append(shortdesc)

    if len(shortdesc_error_list) > 0:
        messagebox.showwarning('EWR Builder', str(len(shortdesc_error_list)) + ' description(s) are longer than 16 chars. Shorten these descriptions and rerun.\n\n' + '\n'.join(shortdesc_error_list))
        return None
    
    treeview_file1.destroy()
    treeview_file2.destroy()

    ewr_merge = ewr_merge[['#LOTID', 'WAFERID', 'CELLNO', 'SHORTDESC', 'LONGDESC']]

    show_treeview_merge(ewr_merge_path)

    TREE_MERGE_DATA['columns'] = list(ewr_merge.columns)
    TREE_MERGE_DATA['show'] = 'headings'
    for column in TREE_MERGE_DATA['columns']:
        TREE_MERGE_DATA.heading(column, text=column)
    ewr_rows = ewr_merge.to_numpy().tolist()
    for row in ewr_rows: # for each row in df, insert into tree view
        TREE_MERGE_DATA.insert('', 'end', values=row)
    
    TREE_MERGE_DATA.column('#LOTID', width=10, stretch=YES)
    TREE_MERGE_DATA.column('WAFERID', width=10, stretch=YES)
    TREE_MERGE_DATA.column('CELLNO', width=10, stretch=YES)
    TREE_MERGE_DATA.column('SHORTDESC', width=10, stretch=YES)
    TREE_MERGE_DATA.column('LONGDESC', width=10, stretch=YES)
    
    print('Merged EWR:')
    print(ewr_merge)
    
    stats_merge(ewr_merge)
    stats_general()
    
    ewr_merge.to_csv(ewr_merge_path, index=False)
    messagebox.showinfo('EWR Builder', 'Complete.\n\n' + 'The file has been saved to: \r' + ewr_merge_path)

    global FILE1 ## ** to be moved into the clear function 
    global FILE2
    FILE1 = None
    FILE2 = None

def clear_merge_ewr():
    global FILE1
    global FILE2
    
    try:    
        FILE1 = None ## ** reset file1 and file2 variables; not sure if this is working
        FILE2 = None
        merge_ewr_page()
        FRAME_MERGE.destroy()
        TREE_MERGE_DATA.delete(*TREE_MERGE_DATA.get_children())
        TREE_MERGE_DATA['columns'] = list(DF_INPUT.columns) ## ** think DF_INPUT is the wrong variable
        FILEPATH_LABEL['text'] = 'File Location: '
    except: 
        return

def stats_merge(dataframe):
    global NUM_UNIQUE_LOTIDS
    global NUM_UNIQUE_WAFERIDS
    global NUM_TOTAL_CELLS
    
    NUM_UNIQUE_LOTIDS = str(len(dataframe['#LOTID'].unique()))
    NUM_UNIQUE_WAFERIDS = str(len(dataframe['WAFERID'].unique()))
    NUM_TOTAL_CELLS = str(len(dataframe['CELLNO'].unique()))
    

## Merge EWRs Page End


## Intialize Main Menu

main_menu_page()


root.mainloop()