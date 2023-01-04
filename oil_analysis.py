import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import constants as c
from functions import custom_round
pd.set_option('mode.chained_assignment', None)

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


def limp_mode_graph(df, x_col, y_col, plot_type, marker, single_plot_t_f, lap_num, color):
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
        plt.plot(x, y, **plot_styles_dict, label=f'Session: {lap_num}')
    plt.autoscale(enable=True, axis='both', tight=None)

    # test Start
    plt.legend(loc='lower right')
    # test End

    try:
        return fig
    except:
        return None


## test (this might be used for oil analysis)
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


def init_oil_analysis(df_list: list, max_oil_temp_diff: int):
    # ** When creating a GUI, we will only need 2 files, 100% oil and x% oil. There will be two
    # buttons to select which is which. Using glob will no longer be needed. We can simply assign
    # csv_files to [file1.csv (100%), file2.csv (x%)]

    # session_names_list = ['100%', 'x%']\

    df_sessions_list = []
    for df in df_list:
        df = round_limp_mode(df)
        
        df_laps_list = split_laps(df)[1:-2] # **
        
        # loop laps to remove outliers
        for index, lap in enumerate(df_laps_list):
            lap = remove_rolling_outliers(lap, c.COOLANT_TEMP_COL, window=c.ROLLING_WINDOW)
            lap = remove_quantile_outliers(lap, c.LO_QUANTILE, c.HI_QUANTILE)
            df_laps_list[index] = lap

        # loop laps to collect hottest average temperature
        avg_temps_list = []
        for lap in df_laps_list:
            temperature = hottest_avg_temp(lap, c.COOLANT_TEMP_COL)
            avg_temps_list.append(temperature)

        hottest_lap_avg = max(avg_temps_list)
        
        # print()
        # print(f'# of Laps: {len(df_laps_list)}')

        usable_laps_list = []
        for lap in df_laps_list:
            min_temp_diff = abs(hottest_lap_avg - lap[c.COOLANT_TEMP_COL].min())
            max_temp_diff = abs(hottest_lap_avg - lap[c.COOLANT_TEMP_COL].max())
            
            # print(f'Min: {lap[c.COOLANT_TEMP_COL].min()}')
            # print(f'Min diff: {min_temp_diff}')
            
            # print(f'Max: {lap[c.COOLANT_TEMP_COL].max()}')
            # print(f'Max diff: {max_temp_diff}')

            # if (min_temp_diff < c.MAX_TEMP_DIFF_FROM_AVG) and (max_temp_diff < c.MAX_TEMP_DIFF_FROM_AVG):
            if (min_temp_diff < max_oil_temp_diff) and (max_temp_diff < max_oil_temp_diff):
                usable_laps_list.append(lap)


        df_good_laps = pd.concat(usable_laps_list)
        df_sessions_list.append(df_good_laps)

    plt.cla() # Removes previous graphs. Shouldnt be needed when we move to Object Oriented
    k = -1
    for df_session in df_sessions_list:
        k+=1
        # session_name = os.path.basename(csv_files[k])
        limp_mode_graph(df_session, c.TIME_COL, c.COOLANT_TEMP_COL, plot_type='line', marker='none', single_plot_t_f=False, lap_num=f'Session: {k+1}', color=c.COLORS_LIST[k])
        # df_session.to_csv(f'session {k}.csv', index=False)
    plt.figure('test1')
    
    
    # loop sessions to set max and min ticks for graph
    max_rpm = []
    min_rpm = []
    for df_session in df_sessions_list:
        min_rpm.append(min(df_session[c.RPM_COL]))
        max_rpm.append(max(df_session[c.RPM_COL]))
    min_rpm = min(min_rpm)
    max_rpm = max(max_rpm)
    

    k = -1
    for df_session in df_sessions_list:
        k+=1
        # session_name = os.path.basename(csv_files[k])
        limp_mode_graph(df_session, c.RPM_COL, c.OIL_PRESS_COL, plot_type='line', marker='none', single_plot_t_f=False, lap_num=f'test 1: {k}', color=c.COLORS_LIST[k])
        # plt.xticks(np.arange(min(df_session[c.RPM_COL]), max(df_session[c.RPM_COL]), 500))
        # plt.xticks(np.arange(custom_round(min(df_session[c.RPM_COL]), 1000), custom_round(max(df_session[c.RPM_COL]), 1000), 500))
        plt.xticks(np.arange(custom_round(min_rpm, 1000), custom_round(max_rpm, 1000), 500))
    plt.figure('test2')
    
    
    sessions_groupby_rpm_list = []
    k = -1
    for df_session in df_sessions_list:
        k+=1
        # session_name = os.path.basename(csv_files[k])

        df_rpm_groupby = df_session.groupby(c.RPM_COL, group_keys=False)[c.OIL_PRESS_COL].mean().reset_index(name=c.OIL_PRESS_COL)
        sessions_groupby_rpm_list.append(df_rpm_groupby)
    
    df_pct_change = pd.merge(sessions_groupby_rpm_list[0], sessions_groupby_rpm_list[1], on=c.RPM_COL)
    df_pct_change['% Change Initial'] = ((df_pct_change[f'{c.OIL_PRESS_COL}_x'] - df_pct_change[f'{c.OIL_PRESS_COL}_x']) / df_pct_change[f'{c.OIL_PRESS_COL}_x']) * 100
    df_pct_change['% Change'] = ((df_pct_change[f'{c.OIL_PRESS_COL}_y'] - df_pct_change[f'{c.OIL_PRESS_COL}_x']) / df_pct_change[f'{c.OIL_PRESS_COL}_x']) * 100

    print(df_pct_change)

    # var1_vs_var2_graph(df_pct_change, c.RPM_COL, '% Change Initial', plot_type='line', marker='none', single_plot_t_f=False, lap_num=os.path.basename(csv_files[0]), color=c.COLORS_LIST[0])
    # var1_vs_var2_graph(df_pct_change, c.RPM_COL, '% Change', plot_type='line', marker='none', single_plot_t_f=False, lap_num=os.path.basename(csv_files[1]), color=c.COLORS_LIST[1])
    limp_mode_graph(df_pct_change, c.RPM_COL, '% Change Initial', plot_type='line', marker='none', single_plot_t_f=False, lap_num=f'test 2: {k}', color=c.COLORS_LIST[0])
    limp_mode_graph(df_pct_change, c.RPM_COL, '% Change', plot_type='line', marker='none', single_plot_t_f=False, lap_num=f'test 3: {k}', color=c.COLORS_LIST[1])


    plt.show()

    return None