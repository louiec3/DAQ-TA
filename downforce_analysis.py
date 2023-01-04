import pandas as pd

import constants as c
from functions import custom_round, stationary_normalization, var1_vs_var2_graph

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
    df_downforce[c.SPEED_COL] = df_downforce[c.SPEED_COL].apply(lambda x: custom_round(x, 1))
    
    return df_downforce



def init_downforce_analysis(df):
    df_data = stationary_normalization(df, c.FL_FORCE_COL, True)
    df_data = stationary_normalization(df, c.FR_FORCE_COL, True)
    df_data = stationary_normalization(df, c.RL_FORCE_COL, True)
    df_data = stationary_normalization(df, c.RR_FORCE_COL, True)
    
    df_downforce = coast_down_data_validation(df_data)

    # plots_list = []
    # for col in FORCE_COLS:
    downforce_plot = var1_vs_var2_graph(df_downforce, c.SPEED_COL, c.DOWNFORCE_COL, plot_type='scatter', marker='o', single_plot_t_f=True)
        # plots_list.append(plot)
    # coastdown_output_pdf = matplotlib.backends.backend_pdf.PdfPages(coastdown_pdf_path)
    # coastdown_output_pdf.savefig(downforce_plot)
    # coastdown_output_pdf.close()

    # export_df_csv(df_downforce, coastdown_output_csv, False)

    return downforce_plot
