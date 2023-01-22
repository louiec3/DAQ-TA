import pandas as pd

import constants as c
import functions as f
import matplotlib.pyplot as plt


# test for coast down (future, make it for coast up as well)
def coast_down_data_validation(df):
    # Check between time interval if there is any throttle or brake input
    df_valid_coast = df[(df[c.THROTTLE_COL] < c.THROTTLE_CONSTANT) & (df[c.FBRAKE_COL] < c.FBRAKE_CONSTANT) 
                    & (df[c.RBRAKE_COL] < c.RBRAKE_CONSTANT) & (df[c.YAW_COL] < c.YAW_CONSTANT)
                    & (df[c.SPEED_COL] > c.MIN_COAST_SPEED)]    
    
    df_FL = df_valid_coast[[c.TIME_COL, c.FL_FORCE_COL, c.SPEED_COL]].rename(columns={c.FL_FORCE_COL: c.DOWNFORCE_COL})
    df_FR = df_valid_coast[[c.TIME_COL, c.FR_FORCE_COL, c.SPEED_COL]].rename(columns={c.FR_FORCE_COL: c.DOWNFORCE_COL})
    df_RL = df_valid_coast[[c.TIME_COL, c.RL_FORCE_COL, c.SPEED_COL]].rename(columns={c.RL_FORCE_COL: c.DOWNFORCE_COL})
    df_RR = df_valid_coast[[c.TIME_COL, c.RR_FORCE_COL, c.SPEED_COL]].rename(columns={c.RR_FORCE_COL: c.DOWNFORCE_COL})
    
    df_downforce = pd.concat([df_FL, df_FR, df_RL, df_RR]).reset_index(drop=True) # on=merge_cols).reset_index(drop=True)#.merge(df_RL, on=merge_cols).merge(df_RR, on=merge_cols).reset_index(drop=True)
    
    df_downforce[c.DOWNFORCE_COL] = df_downforce[c.DOWNFORCE_COL] / c.N_LBF_CONVERSION
    df_downforce[c.SPEED_COL] = df_downforce[c.SPEED_COL].apply(lambda x: f.custom_round(x, 1))
    
    return df_downforce


def init_downforce_analysis(df):
    f.clear_plots()

    df_data = f.stationary_normalization(df, c.FL_FORCE_COL, True)
    df_data = f.stationary_normalization(df, c.FR_FORCE_COL, True)
    df_data = f.stationary_normalization(df, c.RL_FORCE_COL, True)
    df_data = f.stationary_normalization(df, c.RR_FORCE_COL, True)
    
    df_downforce = coast_down_data_validation(df_data)

    fig = f.var1_vs_var2_graph(df_downforce, c.SPEED_COL, c.DOWNFORCE_COL, plot_type='scatter', marker='o', single_plot_t_f=True)
    fig.canvas.manager.set_window_title('Downforce Analysis')

    return fig
