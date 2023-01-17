# To Do:
# - Find a way to name sessions in limpmode graph

import constants as c

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
from scipy.optimize import curve_fit

from os.path import dirname, exists
import os
import datetime as dt

## Different functions need to be used based on the environment type
try: # Test for terminal env
    path_script = dirname(os.path.abspath(__file__)) + '\\'
    output_path = path_script + 'Output' + '\\'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
except: # Assumes notebook env
    path_script = os.path.abspath('') + '/'
    output_path = path_script + 'Output/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

date = dt.datetime.now()
timestamp = date.strftime('%m-%d-%Y_%H-%M-%S')
data_file = path_script + 'Input' + '/data.csv'
oil_files = path_script + 'Input' + '/oil_files'
sectors_file = path_script + 'Input' + '/sectors.csv'
print(path_script)
print(data_file)

coastdown_output_csv = output_path + 'CoastDown_' + timestamp + '.csv'
coastdown_pdf_path = output_path + 'CoastDown_' + timestamp + '.pdf'
# coastdown_output_pdf = matplotlib.backends.backend_pdf.PdfPages(coastdown_pdf_path)

matplotlib.rcParams['figure.figsize'] = (9.5, 5)


def export_df_xlsx(df, writer, sheetname, index_t_f):
    df.to_excel(writer, sheet_name=sheetname, index=index_t_f)


def export_df_csv(df, name, index_t_f):
    df.to_csv(name, index=index_t_f)
    

def custom_round(value, resolution):
    new_val = round(value/resolution)*resolution
    
    return new_val


def format_data(df):
    df = df[0].str.split(',', expand=True)

    # remove default (empty) rows from top of dataframe
    df = df.replace('NaN', np.nan)
    df = df.dropna(how='all', axis=1)
    df = df.drop_duplicates(keep='last').reset_index(drop=True)
    df = df.apply(lambda x: x.str.strip('"'))
    df = df.apply(lambda x: x.str.strip("'"))
    df = format_headers(df)
    
    data_start_index = df.index[(df[c.TIME_COL] == '0') | (df[c.TIME_COL] == '0.000')].tolist()[0]
    df = df.iloc[data_start_index:].reset_index(drop=True)
    df = df.astype(float)

    df = df.dropna(axis=1, how='all')

    return df


def format_headers(df):
    # Rename headers to include units, drop empty column
    # header_row = [x for x in df[0].tolist() if 'Time' in x][-1]
    header_row = [i for i, x in enumerate(df[0].tolist()) if 'Time' in x][-1]
    df = df.iloc[header_row:]
    parameters = df.iloc[0]
    units_list = df.iloc[1]
    new_headers = [f'{param} ({unit})' for param, unit in zip(parameters, units_list)]
    df.columns = new_headers
    
    drop_cols_list = [header for header in new_headers if len(header) < 4]
    df = df.drop(drop_cols_list, axis=1).reset_index(drop=True)

    return df


def locate_variable_col(df):
    # create a variable for our column of interest
    last_col = df.columns[-1]

    return last_col

# ** refactor stationary/normalization functions. Overall rework needed to make this viable. 
# Split the functions up.
def stationary_dataframe(df):
    # **TO DO: Remove outliers of stationary (important when checking for driver inputs; or dont use this func for certain tests like driver inputs at stationary)
    df_count = df.groupby(c.DISTANCE_COL)[c.DISTANCE_COL].count().sort_values(ascending=False)
    df_count = df_count[df_count >= c.MIN_STATIONARY_ENTRIES]
    stationary_list = df_count.keys().tolist()
    df_stationary = df[df[c.DISTANCE_COL].isin(stationary_list)]
    print(df_count)
    df_remove_stationary = df[~df[c.DISTANCE_COL].isin(stationary_list)]

    return df_stationary, df_remove_stationary


def remove_stationary(df):
    df_stationary, df_remove_stationary = stationary_dataframe(df)
    # del df_stationary
    print('=======')
    print(df_stationary)
    print()
    print(df_remove_stationary)
    print('=======')
    return df_remove_stationary


def stationary_normalization(df, var_col, rmv_stationary_bool):
    # For entries of no movement, find the average acceleration. 
    # This will be used as our zero value.
    df_stationary, df_remove_stationary = stationary_dataframe(df)
    stationary_avg = df_stationary[var_col].mean()
    print(f'Stationary {var_col} Avg: {stationary_avg}')    

    if rmv_stationary_bool is True:
        df = df_remove_stationary

    if stationary_avg < 0:
        df[var_col] = df[var_col] + abs(stationary_avg)
    if stationary_avg > 0:
        df[var_col] = df[var_col] - abs(stationary_avg)
    
    return df


def basic_stats(df, var_col, normalize_stationary_bool, rmv_stationary_bool):
    if normalize_stationary_bool is True and rmv_stationary_bool is False:
        df = stationary_normalization(df, var_col, False)
    if normalize_stationary_bool is True and rmv_stationary_bool is True:
        df = stationary_normalization(df, var_col, True)
    elif normalize_stationary_bool is False and rmv_stationary_bool is True:
        df = remove_stationary(df)
    

    df_basic_stats = df[var_col].describe(percentiles=c.PERCENTILE_LIST)
    df_basic_stats = df_basic_stats.to_frame()
    df_basic_stats['Stats'] = c.STATS_LABELS

    first_column = df_basic_stats.pop('Stats')
    df_basic_stats.insert(0, 'Stats', first_column)
        

    return df_basic_stats


def var1_vs_var2_graph(df, x_col, y_col, plot_type, marker, single_plot_t_f):
    if single_plot_t_f is True:
        fig = plt.figure()
    plt.style.use('ggplot')
    plot_styles_dict = {
        'color': 'steelblue',
        'marker': marker
    }
    title = f'{y_col} vs {x_col}'
    # print(df[[x_col, y_col]])
    df_plot = df[[x_col, y_col]]
    
    # df_avg = df_plot # use this to demonstrate variation of rpm and press without average
    df_avg = df_plot.groupby(x_col, group_keys=False)[y_col].mean().reset_index(name=y_col)

    x = df_avg[x_col] 
    y = df_avg[y_col]

    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(title)

    if plot_type.lower() == 'scatter':
        plt.scatter(x, y, **plot_styles_dict)
    elif plot_type.lower() == 'line':
        plt.plot(x, y, **plot_styles_dict, label=f'Lap')
    plt.autoscale(enable=True, axis='both', tight=None)

    def func1(x, a, b, c):
        return a*x**2+b*x+c
    params, _ = curve_fit(func1, x, y)
    a, b, c = params[0], params[1], params[2]  
    yfit1 = a*x**2+b*x+c      
    plt.plot(x, yfit1, label=f'y={custom_round(a, .001)}*x^2+{custom_round(b, .001)}*x+{custom_round(c, .001)}')
    plt.legend(loc='lower right')

    try:
        return fig
    except:
        return None


def subtract_car_weight(df, var_col):
    df_new = df[var_col] - c.CAR_WEIGHT

    return df_new


def load_sectors_csv():
    if exists(sectors_file): 
        df = pd.read_csv(sectors_file)
        df = df.replace('NaN', np.nan).dropna(how='all')
    else:
        print('No sectors.csv file found. (throw exception for if there are no vaid entries')
        quit()

    return df
