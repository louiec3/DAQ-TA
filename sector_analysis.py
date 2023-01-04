import pandas as pd

import constants as c
from functions import stationary_normalization, remove_stationary


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



def sector_dataframe(df1, df2):
    ## convert time to seconds (start and end time vars are given as mm:ss.ms, csv reads only ss.ms)
    
    sectors_cellA2 = str(df2.iloc[0]['Sector Start']) # ** covert to constant
    print(f'A2: {sectors_cellA2}')

    if ':' in sectors_cellA2:
        print('Time Sectors')
        start_list, end_list = sector_times(df2)
        df_list = []
        for start_time, end_time in zip(start_list, end_list):
            # start_time = round(start, 1)
            # end_time = round(end, 1)
            df_sector_temp = df1[(df1[c.TIME_COL] >= start_time) & (df1[c.TIME_COL] <= end_time)]
            df_list.append(df_sector_temp)
    else:
        print('Distance Sectors')
        start_list, end_list = sector_distances(df2)
        df_list = []
        for start_distance, end_distance in zip(start_list, end_list):
            df_sector_temp = df1[(df1[c.DISTANCE_COL] >= start_distance) & (df1[c.DISTANCE_COL] <= end_distance)]
            df_list.append(df_sector_temp)
        
    df_all_sectors = pd.concat(df_list)
    
    return df_all_sectors




def init_sector_analysis(df_data, df_sectors, col, normalize_stationary_bool, rmv_stationary_bool):
    # Sector analysis by time interval
    # ** Future: Add Time or Distance interval 
    # (Distance could be easier since corners will always be the same distance from 
    # the start becon assuming there are no off tracks)
    print(normalize_stationary_bool)
    print(rmv_stationary_bool)
    
    df_sector_data = sector_dataframe(df_data, df_sectors)
    
    if normalize_stationary_bool is True:
        print('Normalizing data')
        df_sector_data = stationary_normalization(df_sector_data, col, rmv_stationary_bool)
        df_corner_stats = sector_stats(df_sector_data, col)
        
        return df_corner_stats
    
    elif normalize_stationary_bool is False and rmv_stationary_bool is True:
        print('Removing Stationary Only')
        df_sector_data = remove_stationary(df_sector_data)
        df_corner_stats = sector_stats(df_sector_data, col)

        return df_corner_stats
    
    else:
        print('Raw Data')
        print(df_sector_data)
        df_corner_stats = sector_stats(df_sector_data, col)

        return df_corner_stats

