import matplotlib.pyplot as plt
import pandas as pd

import constants as c
import functions as f

def convert_to_seconds(df, col):
    df['Min'] = df[col].str.split(':').str[0].astype(int)
    df['Sec'] = df[col].str.split(':').str[1]
    df['Sec'] = df['Sec'].str.split('.').str[0].astype(int)
    df['MilliSec'] = df[col].str.split('.').str[1].astype(int).apply(lambda x: x*10**-len(str(abs(x))))
    df['TotalSec'] = df['Min']*60 + df['Sec'] + df['MilliSec']

    df_interval = df['TotalSec']

    return df_interval


def sector_times(df):
    df_start = convert_to_seconds(df, 'Sector Start')
    df_end = convert_to_seconds(df, 'Sector End')
    
    start_list = df_start.tolist()
    end_list = df_end.tolist()
    
    return start_list, end_list


def sector_distances(df):
    columns_list = df.columns    
    start_list = df[columns_list[0]].tolist()
    end_list = df[columns_list[1]].tolist()
    
    return start_list, end_list


def sector_stats(df, var_col):
    basic_stats_list = df[var_col].describe(percentiles=c.PERCENTILE_LIST)
    basic_stats_list = basic_stats_list.to_list()

    sigma = df[var_col].std()
    sigma2 = sigma*2
    sigma3 = sigma*3
    sigmas_list = [sigma2, sigma3]
    print(f'{sigmas_list} {type(sigmas_list)}')
    print(f'{basic_stats_list} {type(basic_stats_list)}')
    
    basic_stats_list.extend(sigmas_list)
    print(basic_stats_list)
    df_basic_stats = pd.DataFrame({'Values': basic_stats_list})

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



def sectors_dataframe(df1, df2):
    # convert time to seconds (start and end time vars are given as mm:ss.ms, csv reads only ss.ms)

    sectors_cellA2 = str(df2.iloc[0]['Sector Start']) # ** covert to constant
    print(f'A2: {sectors_cellA2}')

    if ':' in sectors_cellA2:
        print('Time Sectors')
        start_list, end_list = sector_times(df2)
        df_sectors_list = []
        for start_time, end_time in zip(start_list, end_list):
            # start_time = round(start, 1)
            # end_time = round(end, 1)
            df_sector_temp = df1[(df1[c.TIME_COL] >= start_time) & (df1[c.TIME_COL] <= end_time)]
            df_sectors_list.append(df_sector_temp)
    else:
        print('Distance Sectors')
        start_list, end_list = sector_distances(df2)
        df_sectors_list = []
        for start_distance, end_distance in zip(start_list, end_list):
            df_sector_temp = df1[(df1[c.DISTANCE_COL] >= start_distance) & (df1[c.DISTANCE_COL] <= end_distance)]
            df_sectors_list.append(df_sector_temp)
        
    df_all_sectors = pd.concat(df_sectors_list)
    
    return df_sectors_list, df_all_sectors


def annotate_max(df, var_col, ax):
    x = c.GPS_LATITUDE_COL
    y = c.GPS_LONGITUDE_COL

    max_val_index = df[var_col].idxmax()
    max_val = df.iloc[max_val_index][var_col]
    x_max = df.iloc[max_val_index][x]
    y_max = df.iloc[max_val_index][y]
    x_coord = ax.get_xlim()[0]
    y_coord = ax.get_ylim()[1]

    bbox_args = dict(boxstyle="round", fc="0.8")
    arrow_args = dict(arrowstyle="->")
    annotation = ax.annotate(f'Max: {max_val}',
                    xy=(x_max, y_max),
                    xytext=(x_coord, y_coord),
                    ha="left", va="bottom",
                    bbox=bbox_args,
                    arrowprops=arrow_args)
    annotation.draggable()

    return None


def plot_trackmap(df_data, df_sectors, var_col):
    x = c.GPS_LATITUDE_COL
    y = c.GPS_LONGITUDE_COL

    df_sectors_list, df_all_sectors = sectors_dataframe(df_data, df_sectors)

    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title('Track Map')

    plt.title(f'Trackmap: {var_col}')
    ax.plot(df_data[x], df_data[y], color='lightgrey', marker='.', )

    bbox_args = dict(boxstyle="round", fc="black")
    arrow_args = dict(arrowstyle="->")
    annotation = ax.annotate(text='',
                    xy=(df_data[x][4], df_data[y][4]),
                    xytext=(df_data[x][0], df_data[y][0]),
                    ha="left", va="bottom",
                    bbox=bbox_args,
                    arrowprops=arrow_args)

    i=0
    for sector, new_color in zip(df_sectors_list, c.COLORS_LIST):
        i+=1
        ax.plot(sector[x], sector[y], color=new_color, marker='.', label=f'Sector {i}')
        ax.legend(loc='upper right')

    annotate_max(df_all_sectors, var_col, ax)

    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.show()

    return fig
    
def init_sector_analysis(df_data, df_sectors, var_col, normalize_stationary_bool, rmv_stationary_bool):
    f.clear_plots()
    # Sector analysis by time interval
    # ** Future: Add Time or Distance interval 
    # (Distance could be easier since corners will always be the same distance from 
    # the start becon assuming there are no off tracks)
    print(normalize_stationary_bool)
    print(rmv_stationary_bool)
    
    _, df_sector_data = sectors_dataframe(df_data, df_sectors)
    
    if normalize_stationary_bool is True:
        print('Normalizing data')
        df_sector_data = f.stationary_normalization(df_sector_data, var_col, rmv_stationary_bool)
        df_corner_stats = sector_stats(df_sector_data, var_col)
        
    elif normalize_stationary_bool is False and rmv_stationary_bool is True:
        print('Removing Stationary Only')
        df_sector_data = f.remove_stationary(df_sector_data)
        df_corner_stats = sector_stats(df_sector_data, var_col)

    else:
        print('Raw Data')
        print(df_sector_data)
        df_corner_stats = sector_stats(df_sector_data, var_col)

    if c.GPS_LATITUDE_COL and c.GPS_LONGITUDE_COL in df_data.columns:
        # f.clear_plots()
        fig = plot_trackmap(df_data, df_sectors, var_col)

    elif c.GPS_LATITUDE_COL_2 and c.GPS_LONGITUDE_COL_2 in df_data.columns:
        # f.clear_plots()
        fig = plot_trackmap(df_data, df_sectors, var_col)


    return df_corner_stats