import constants as c
from gui import var_col_choice, normalize_stationary_bool, rmv_stationary_bool 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf

from os.path import dirname, exists
import os
import datetime as dt
import sys
import glob

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

def prompt_input_options(option_list):
    # Use when a user must select an option
    valid_list = [x+1 for x in range(len(option_list))]
    
    i = 0
    for option in option_list:
        i+=1
        print(f'({i}) {option}')

    while True:
        try:
            value = int(input('Select an option: '))
        except ValueError:
            print('Please enter a valid option.')
            continue

        if value not in valid_list:
            print('Please enter a valid option.')
            continue
        else:
            break
    
    print()
    user_choice = option_list[value-1]

    return user_choice  


def prompt_input(prompt):
    # Used when any value is needed from user
    while True:
        try:
            value = input(prompt).strip()
        except ValueError:
            print('Please enter a value.')
            continue

        if value is None or value == '':
            print('Please enter a value.')
            continue
        else:
            break

    return value


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


def stationary_dataframe(df):
    # TO DO: Remove outliers of stationary (important when checking for driver inputs; or dont use this func for certain tests like driver inputs at stationary)
    df_count = df.groupby(c.DISTANCE_COL)[c.DISTANCE_COL].count().sort_values(ascending=False)
    df_count = df_count[df_count >= c.MIN_STATIONARY_ENTRIES]
    stationary_list = df_count.keys().tolist()
    df_stationary = df[df[c.DISTANCE_COL].isin(stationary_list)]

    df_remove_stationary = df[~df[c.DISTANCE_COL].isin(stationary_list)]

    return df_stationary, df_remove_stationary


def stationary_normalization(df, var_col, true_false):
    # For entries of no movement, find the average acceleration. 
    # This will be used as our zero value.
    df_stationary, df_remove_stationary = stationary_dataframe(df)
    stationary_avg = df_stationary[var_col].mean()
    print(f'Stationary {var_col} Avg: {stationary_avg}')    

    if true_false is True:
        df = df_remove_stationary

    if stationary_avg < 0:
        df[var_col] = df[var_col] + abs(stationary_avg)
    if stationary_avg > 0:
        df[var_col] = df[var_col] - abs(stationary_avg)
    
    # print(df_remove_stationary)
    
    return df


def basic_stats(df, var_col):
    df_basic_stats = df[var_col].describe(percentiles=c.PERCENTILE_LIST)
    
    return df_basic_stats


def var1_vs_var2_graph(df, x_col, y_col, plot_type, marker, single_plot_t_f, lap_num, color):
    if single_plot_t_f is True:
        fig = plt.figure()
    plt.style.use('ggplot')
    plot_styles_dict = {
        'color': color,
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
        plt.plot(x, y, **plot_styles_dict, label=f'Lap {lap_num}')
    plt.autoscale(enable=True, axis='both', tight=None)
    # plt.show()

    # test Start
    plt.legend(loc='lower right')
    # test End

    try:
        return fig
    except:
        return None


def limp_mode_graph():
    
    
    return None


def sector_dataframe_v2(df1, df2):
    ## convert time to seconds (start and end time vars are given as mm:ss.ms, csv reads only ss.ms)
    start_list, end_list = sector_times(df2)
    df_list = []
    for start, end in zip(start_list, end_list):
        start_time = round(start, 1)
        end_time = round(end, 1)
        df_sector_temp = df1[(df1[c.TIME_COL] >= start_time) & (df1[c.TIME_COL] <= end_time)]
        df_list.append(df_sector_temp)
    
    df_all_sectors = pd.concat(df_list)
    
    return df_all_sectors


def sector_stats_v2(df, var_col):
    df_basic_stats = df[var_col].describe(percentiles=c.PERCENTILE_LIST)
    
    # mean = df[var_col].mean()
    sigma = df[var_col].std()
    sigma2 = sigma*2
    sigma3 = sigma*3

    # df_outliers_sigma2 = df[(df[var_col] <= mean+sigma2) & (df[var_col] >= mean+sigma2)]
    # df_outliers_sigma3 = df[(df[var_col] >= sigma3) & (abs(df[var_col]) <= mean)]
    
    # df_sigma1 = df[((df[var_col] - df[var_col].mean()) / df[var_col].std()).abs() < 1]
    
    df_outliers_sigma2 = df[((df[var_col] - df[var_col].mean()) / df[var_col].std()).abs() > 2]
    df_outliers_sigma3 = df[((df[var_col] - df[var_col].mean()) / df[var_col].std()).abs() > 3]

    print()
    print('Sector Stats:')
    print(f'Sigma 1: {sigma}')
    print(f'Sigma 2: {sigma2}')
    print(f'Sigma 3: {sigma3}')
    print()
    
    print('Sigma2 Outliers:')
    if len(df_outliers_sigma2) > 0:
        print(df_outliers_sigma2)
    else:
        print('No outliers.')
    
    print()
    
    print('Sigma3 Outliers:')
    if len(df_outliers_sigma3) > 0:
        print(df_outliers_sigma3)
    else:
        print('No outliers.\n')
    # print(df_outliers_sigma3)

    return df_basic_stats

def split_laps(df):
    index_list = df.index[df[c.TIME_COL] == 0].tolist()
    index_list.append(len(df))

    df_list = []
    n = 1
    for i in index_list:
        df_temp = df.loc[i:index_list[n]-1]
        df_list.append(df_temp)
        
        n+=1
        if n == len(index_list):
            break
    
    return df_list


def convert_to_seconds(df, col):
    df['Min'] = df[col].str.split(':').str[0].astype(int)
    df['Sec'] = df[col].str.split(':').str[1]
    df['Sec'] = df['Sec'].str.split('.').str[0].astype(int)
    df['MilliSec'] = df[col].str.split('.').str[1].astype(int).apply(lambda x: x*10**-len(str(abs(x))))
    df['TotalSec'] = df['Min']*60 + df['Sec'] + df['MilliSec']

    df_interval = df['TotalSec']

    return df_interval


def sector_times(df):
    df_start = convert_to_seconds(df, 'Corner Start')
    df_end = convert_to_seconds(df, 'Corner End')
    
    start_list = df_start.tolist()
    end_list = df_end.tolist()
    
    return start_list, end_list


# test for coast down (future, make it for coast up as well)
def coast_down(df):
    # Check between time interval if there is any throttle or brake input
    # df_coast = sector_dataframe_v2(df, df_corner_times) # Is there a need to use sectors?       
    df_valid_coast = df[(df[c.THROTTLE_COL] < c.THROTTLE_CONSTANT) & (df[c.FBRAKE_COL] < c.FBRAKE_CONSTANT) 
                    & (df[c.RBRAKE_COL] < c.RBRAKE_CONSTANT) & (df[c.YAW_COL] < c.YAW_CONSTANT)
                    & (df[c.SPEED_COL] > c.MIN_COAST_SPEED)]    
    # df_valid_coast.to_csv('speedtest1.csv', index=False)
    
    df_FL = df_valid_coast[[c.TIME_COL, c.FL_FORCE_COL, c.SPEED_COL]].rename(columns={c.FL_FORCE_COL: c.DOWNFORCE_COL})
    df_FR = df_valid_coast[[c.TIME_COL, c.FR_FORCE_COL, c.SPEED_COL]].rename(columns={c.FR_FORCE_COL: c.DOWNFORCE_COL})
    df_RL = df_valid_coast[[c.TIME_COL, c.RL_FORCE_COL, c.SPEED_COL]].rename(columns={c.RL_FORCE_COL: c.DOWNFORCE_COL})
    df_RR = df_valid_coast[[c.TIME_COL, c.RR_FORCE_COL, c.SPEED_COL]].rename(columns={c.RR_FORCE_COL: c.DOWNFORCE_COL})
    
    df_downforce = pd.concat([df_FL, df_FR, df_RL, df_RR]).reset_index(drop=True)
    df_downforce[c.DOWNFORCE_COL] = df_downforce[c.DOWNFORCE_COL] / c.N_LBF_CONVERSION

    # df_downforce = df_FL.merge(df_FL, on=merge_cols).reset_index(drop=True)#.merge(df_RL, on=merge_cols).merge(df_RR, on=merge_cols).reset_index(drop=True)
    df_downforce = pd.concat([df_FL, df_FR, df_RL, df_RR]).reset_index(drop=True) # on=merge_cols).reset_index(drop=True)#.merge(df_RL, on=merge_cols).merge(df_RR, on=merge_cols).reset_index(drop=True)
    
    df_downforce[c.DOWNFORCE_COL] = df_downforce[c.DOWNFORCE_COL] / c.N_LBF_CONVERSION
    df_downforce[c.SPEED_COL] = df_downforce[c.SPEED_COL].apply(lambda x: custom_round(x, 1))
    # df_downforce.to_csv('speedtest2.csv', index=False)


    return df_downforce


def round_limp_mode(df):
    df[c.RPM_COL] = df[c.RPM_COL].apply(lambda x: custom_round(x, 100))
    df[c.OIL_PRESS_COL] = df[c.OIL_PRESS_COL].apply(lambda x: custom_round(x, .25))
    df[c.OIL_TEMP_COL] = df[c.OIL_TEMP_COL].apply(lambda x: custom_round(x, 1))
    df[c.COOLANT_TEMP_COL] = df[c.COOLANT_TEMP_COL].apply(lambda x: custom_round(x, 1))

    return df
    

def remove_rolling_outliers(df, col, window):
    df['median']= df[col].rolling(window).median()
    df['mean']= df[col].rolling(window).mean()
    df['std'] = df[col].rolling(window).std()
    
    df_new = df[(df[col] <= df['median'] + c.ROLLING_SIGMA*df['std']) & (df[col] >= df['median'] - c.ROLLING_SIGMA*df['std'])]

    return df_new


def remove_quantile_outliers(df, low, high):
    q_low = df[c.COOLANT_TEMP_COL].quantile(low)
    q_hi = df[c.COOLANT_TEMP_COL].quantile(high)
    df_new = df[(df[c.COOLANT_TEMP_COL] <= q_hi) & (df[c.COOLANT_TEMP_COL] >= q_low)]

    return df_new


def hottest_avg_temp(df, temperature_col):
    avg_temp = df[temperature_col].mean()

    return avg_temp


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


## test
def pct_change_graph(df, x_col, y_col, lap_num, color):
    plt.style.use('ggplot')
    plot_styles_dict = {
        'color': color,
        'marker': ''
    }
    df_plot = df[[x_col, y_col]]

    # df_avg = df_plot # use this to demonstrate variation of rpm and press without average
    df_avg = df_plot.groupby(x_col, group_keys=False)[y_col].mean().reset_index(name=y_col)

    title = f'{y_col} vs {x_col}'
    x = df_avg[x_col] 
    y = df_avg[y_col]

    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(title)

    plt.plot(x, y, **plot_styles_dict, label=f'Lap {lap_num}')
    plt.legend()

    return None
## test




######### user functions start ##############
# ** make new file
def limp_mode(df_list: list):
    # ** When creating a GUI, we will only need 2 files, 100% oil and x% oil. There will be two
    # buttons to select which is which. Using glob will no longer be needed. We can simply assign
    # csv_files to [file1.csv (100%), file2.csv (x%)]

    # csv_files = glob.glob(os.path.join(input_path + 'oil_files', 'oil*.csv'))
    # print(csv_files)

    # oil_100 = [file for file in csv_files if '100' in file][0]
    # csv_files.remove(oil_100)
    # csv_files.insert(0, oil_100)

    df_sessions_list = []
    for f in csv_files:
        df_temp = pd.read_fwf(f, header=None, encoding='ISO-8859-1')

        df_temp = format_data(df_temp)
        df_temp = round_limp_mode(df_temp)
        df_laps_list = split_laps(df_temp)[1:-2] # **
        
        for index, lap in enumerate(df_laps_list):
            lap = remove_rolling_outliers(lap, c.COOLANT_TEMP_COL, window=c.ROLLING_WINDOW)
            lap = remove_quantile_outliers(lap, c.LO_QUANTILE, c.HI_QUANTILE)
            df_laps_list[index] = lap

        avg_temps_list = []
        for lap in df_laps_list:
            temperature = hottest_avg_temp(lap, c.COOLANT_TEMP_COL)
            avg_temps_list.append(temperature)

        hottest_lap_avg = max(avg_temps_list)

        # print(f'# of Laps: {len(df_laps_list)}')
        usable_laps_list = []
        for lap in df_laps_list:
            min_temp_diff = abs(hottest_lap_avg - lap[c.COOLANT_TEMP_COL].min())
            max_temp_diff = abs(hottest_lap_avg - lap[c.COOLANT_TEMP_COL].max())
            
            # print(f'Min: {lap[c.COOLANT_TEMP_COL].min()}')
            # print(f'Min diff: {min_temp_diff}')
            
            # print(f'Max: {lap[c.COOLANT_TEMP_COL].max()}')
            # print(f'Max diff: {max_temp_diff}')

            if (min_temp_diff < c.MAX_TEMP_DIFF_FROM_AVG) and (max_temp_diff < c.MAX_TEMP_DIFF_FROM_AVG):
                usable_laps_list.append(lap)


        df_good_laps = pd.concat(usable_laps_list)
        df_sessions_list.append(df_good_laps)

    c = -1
    for df_session in df_sessions_list:
        c+=1
        session_name = os.path.basename(csv_files[c])
        var1_vs_var2_graph(df_session, c.TIME_COL, c.COOLANT_TEMP_COL, plot_type='line', marker='none', single_plot_t_f=False, lap_num=session_name, color=c.colors_list[c])
    plt.figure()
    
    
    c = -1
    for df_session in df_sessions_list:
        c+=1
        session_name = os.path.basename(csv_files[c])
        var1_vs_var2_graph(df_session, c.RPM_COL, c.OIL_PRESS_COL, plot_type='line', marker='none', single_plot_t_f=False, lap_num=session_name, color=c.colors_list[c])
        # plt.xticks(np.arange(min(df_session[c.RPM_COL]), max(df_session[c.RPM_COL]), 500))
        plt.xticks(np.arange(custom_round(min(df_session[c.RPM_COL]), 1000), custom_round(max(df_session[c.RPM_COL]), 1000), 500))
    plt.figure()
    
    
    sessions_groupby_rpm_list = []
    c = -1
    for df_session in df_sessions_list:
        c+=1
        session_name = os.path.basename(csv_files[c])

        df_rpm_groupby = df_session.groupby(c.RPM_COL, group_keys=False)[c.OIL_PRESS_COL].mean().reset_index(name=c.OIL_PRESS_COL)
        sessions_groupby_rpm_list.append(df_rpm_groupby)
    
    df_pct_change = pd.merge(sessions_groupby_rpm_list[0], sessions_groupby_rpm_list[1], on=c.RPM_COL)
    df_pct_change['% Change Initial'] = ((df_pct_change[f'{c.OIL_PRESS_COL}_x'] - df_pct_change[f'{c.OIL_PRESS_COL}_x']) / df_pct_change[f'{c.OIL_PRESS_COL}_x']) * 100
    df_pct_change['% Change'] = ((df_pct_change[f'{c.OIL_PRESS_COL}_y'] - df_pct_change[f'{c.OIL_PRESS_COL}_x']) / df_pct_change[f'{c.OIL_PRESS_COL}_x']) * 100

    print(df_pct_change)

    plt.figure()
    var1_vs_var2_graph(df_pct_change, c.RPM_COL, '% Change Initial', plot_type='line', marker='none', single_plot_t_f=False, lap_num=os.path.basename(csv_files[0]), color=c.colors_list[0])
    var1_vs_var2_graph(df_pct_change, c.RPM_COL, '% Change', plot_type='line', marker='none', single_plot_t_f=False, lap_num=os.path.basename(csv_files[1]), color=c.colors_list[1])


    plt.show()

    return None


def sector_analysis():
        # Sector analysis by time interval
        # ** Future: Time or Distance interval 
        # (Distance could be easier since corners will always be the same distance from 
        # the start becon assuming there are no off tracks)
        df_corner_times = load_sectors_csv()
        df_corners = sector_dataframe_v2(df_data, df_corner_times)
        
        # normalization_input = prompt_input_options(normalization_options_list)
        # if normalization_input == normalization_options_list[0]:
        df_data = stationary_normalization(df_data, variable_col, rmv_stationary_tf)
        
        # df_corner_stats = corner_stats_v2(df_corners, variable_col)
        # print('Corner Stats')
        # print(df_corner_stats)


def downforce_analysis(df):
        # Coast down analysis
        # print(script_options_list[1])

        # normalization_input = prompt_input_options(normalization_options_list)
        # if normalization_input == normalization_options_list[0]:
        df_data = stationary_normalization(df, c.FL_FORCE_COL, rmv_stationary_tf)
        df_data = stationary_normalization(df, c.FR_FORCE_COL, rmv_stationary_tf)
        df_data = stationary_normalization(df, c.RL_FORCE_COL, rmv_stationary_tf)
        df_data = stationary_normalization(df, c.RR_FORCE_COL, rmv_stationary_tf)
        
        df_downforce = coast_down(df_data)

        # plots_list = []
        # for col in FORCE_COLS:
        plot = var1_vs_var2_graph(df_downforce, c.SPEED_COL, c.DOWNFORCE_COL, plot_type='scatter', marker='o', single_plot_t_f=True)
            # plots_list.append(plot)
        
        coastdown_output_pdf = matplotlib.backends.backend_pdf.PdfPages(coastdown_pdf_path)
        coastdown_output_pdf.savefig(plot)
        coastdown_output_pdf.close()

        export_df_csv(df_downforce, coastdown_output_csv, False)


def session_analysis(df):
        # Basic stats analysis
        # print(script_options_list[2])

        # normalization_input = prompt_input_options(normalization_options_list)
        # if normalization_input == normalization_options_list[0]:
            # df_data = stationary_normalization(df_data, variable_col, rmv_stationary_tf)
        
        df_stats = basic_stats(df, variable_col)
        # print()
        # print(f'Data for: {variable_col}')
        # print(df_data)
        # print()
        print('\nStatistics')
        print(df_stats)
        print()



