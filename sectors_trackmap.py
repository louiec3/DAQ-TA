import pandas as pd
import matplotlib.pyplot as plt
from functions import *
import constants as c

# this is the same as sectors_dataframe except it does not concat the datafamaes into 1 dataframe. 
# Keeps them separate so we can loop through each and plot them in different colors.
def sectors(df1, df2):
    ## convert time to seconds (start and end time vars are given as mm:ss.ms, csv reads only ss.ms)
    
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
    
    # return df_all_sectors
    return df_sectors_list

df = pd.read_csv(r'C:\Users\louie\Desktop\FSAE_GUI\venv\Test_Input\GPS_Data_2684.csv')
df_sectors = pd.read_csv(r'C:\Users\louie\Desktop\FSAE_GUI\venv\Test_Input\sectors_distance.csv')

sectors_list = sectors(df, df_sectors)
print(sectors_list)

x = 'GPS_Latitude'
y = 'GPS_Longitude'

plt.plot(df[x], df[y], color='lightgrey', marker='.', )

i = 1
for sector, new_color in zip(sectors_list, c.COLORS_LIST):
    plt.plot(sector[x], sector[y], color=new_color, marker='.', label=f'Sector {i}')
    plt.legend(loc='lower right')
    i+=1
    
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())
plt.show()