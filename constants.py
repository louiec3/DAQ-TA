# File saving variables
import os
from os.path import dirname
from datetime import datetime
import sys

date = datetime.now()
timestamp = date.strftime('%m-%d-%Y_%H-%M-%S')

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    script_path = os.path.dirname(sys.executable) + '\\'
elif __file__:
    script_path = os.path.dirname(__file__) + '\\'

print(script_path)

output_folder = script_path + 'Output' + '\\'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
session_analysis_path = output_folder + '/session_analysis_' + timestamp + '.csv'
sector_analysis_path = output_folder + '/sector_analysis_' + timestamp + '.csv'


# Data filtering/processing constants
MIN_STATIONARY_ENTRIES = 50 # Minimum number of occurances (at a distance) to be considered stationary
ROWS_TO_SKIP = 13 # Used to separate # deprecated
PERCENTILE_LIST = [.05, .10, .25, .50, .75, .90, .95]
STATS_LABELS = ['Count', 'Mean', 'Sigma', 'Min', '5%', '10%', '25%', '50%', '75%', '90%', '95%', 'Max']
SECTOR_STATS_LABELS = ['Count', 'Mean', 'Sigma', 'Min', '5%', '10%', '25%', '50%', '75%', '90%', '95%', 'Max', 'Sigma 2', 'Sigma 3']

CAR_WEIGHT = 0

THROTTLE_CONSTANT = 10
FBRAKE_CONSTANT = 30
RBRAKE_CONSTANT = 30
YAW_CONSTANT = 4
MIN_COAST_SPEED = 25
N_LBF_CONVERSION = 4.448 # Newtons to Lbf conversion factor

# Race studio column names including units
TIME_COL = 'Time (sec)'
DISTANCE_COL = 'Distance (km)'

GPS_LATITUDE_COL = 'GPS_Latitude (#)'
GPS_LONGITUDE_COL = 'GPS_Longitude (#)'

THROTTLE_COL = 'S8_tps1 (%)'
FBRAKE_COL = 'F_Brake_Press (PSI)'
RBRAKE_COL = 'R_Brake_Pres (PSI)'
YAW_COL = 'YawRate (deg/s)'

SPEED_COL = 'GPS_Speed (mph)'
RPM_COL = 'S8_RPM (rpm)'

OIL_PRESS_COL = 'S8_eop (PSI)'
OIL_TEMP_COL = 'S8_eot (°F)'
COOLANT_TEMP_COL = 'S8_ect1 (°F)'

DOWNFORCE_COL= 'Downforce (lbf)'
FL_FORCE_COL = 'Front_Left_Forc (#)'
FR_FORCE_COL = 'Front_Right_Forc (#)'
RL_FORCE_COL = 'Rear_Left_Force (#)'
RR_FORCE_COL = 'Rear_Right_Force (#)'
FORCE_COLS = [FL_FORCE_COL, FR_FORCE_COL, RL_FORCE_COL, RR_FORCE_COL]

FR_PULL_ROD_FORC_COL = 'FR_Pull_Rod_Forc (#)'

# Limp Mode Outlier Removal Constants
ROLLING_SIGMA = 2
ROLLING_WINDOW = 75

LO_QUANTILE = 0.01
HI_QUANTILE = 0.99

MAX_TEMP_DIFF_FROM_AVG = 7

# Matplotlib line colors
COLORS_LIST = ['red', 'blue', 'green', 'black', 'yellow', 'purple', 'orange', 'slategrey', 'teal', 'lime', 'gold', 'aqua', 'pink', 'fuchsia', 'aquamarine', 'royalblue', 'bisque', 'darkviolet']