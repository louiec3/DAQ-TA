# Data filtering/processing constants
MIN_STATIONARY_ENTRIES = 50 # Minimum number of occurances (at a distance) to be considered stationary
ROWS_TO_SKIP = 13 # Used to separate # deprecated
PERCENTILE_LIST = [.05, .10, .25, .50, .75, .90, .95]
STATS_LABELS = ['count', 'mean', 'std', 'min', '5%', '10%', '25%', '50%', '75%', '90%', '95%', 'max']

CAR_WEIGHT = 490

THROTTLE_CONSTANT = 10
FBRAKE_CONSTANT = 30
RBRAKE_CONSTANT = 30
YAW_CONSTANT = 4
MIN_COAST_SPEED = 25
N_LBF_CONVERSION = 4.448 # Newtons to Lbf conversion factor

# Race studio column names including units
TIME_COL = 'Time (sec)'
DISTANCE_COL = 'Distance (km)'

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



# Outlier Removal Constants
ROLLING_SIGMA = 2
ROLLING_WINDOW = 75

LO_QUANTILE = 0.01
HI_QUANTILE = 0.99

MAX_TEMP_DIFF_FROM_AVG = 7

# Matplotlib line colors
colors_list = ['red', 'blue', 'green', 'black', 'yellow', 'purple', 'orange', 'slategrey', 'teal', 'lime', 'gold', 'aqua', 'pink', 'fuchsia', 'aquamarine', 'royalblue', 'bisque', 'darkviolet']