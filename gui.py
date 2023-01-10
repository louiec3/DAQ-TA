# To do:
# - Create function to create treeviews (decluter) DONE
# - Create widget to toggle limp mode parameters DONE
# - Figure out how to make the Graph buttons work individually for oil analysis
# - Implement % change graph DONE(?)
# - Restructure plotting functions... way too cluttered with too many arguments. Make individual plots
# - For functions.py, create separate files for unique functions (downforce, oil...) DONE
# - Look into classes and reformatting GUI structure (backlog)

# Bugs
# Global variables... 
# - When you run downforce then oil analysis, the downforce plot is
# visible in the first oil graph
# - Export button only exports once... B/c the date.now func only runs at startup

## Note
# Look into storing text in a txt file and references that text
# ie an about page could contain a paragraph and not be needed in the code itself
## Note end

####################################################################
# UConn Formula SAE
# Data Acquisition - Multifunction Analysis Tool
# Date Uploaded: __/__/____
# A tool to automate data analysis for the UConn FSAE team.
# Louis Cundari III
# louis.cundari@uconn.edu | louiscundari3@outlook.com
####################################################################

from functions import *
from sector_analysis import init_sector_analysis
from downforce_analysis import init_downforce_analysis
from oil_analysis import init_oil_analysis
import constants as c

import tkinter as tk
from tkinter import * # remove * and add used functions later
from tkinter import ttk, filedialog, messagebox, simpledialog
# from os.path import dirname, abspath 
# import os
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np

root = Tk()

root.title('Multifunction Staistics Tool')
# root.state('zoomed') # expands window

window_height = 600
window_width = 700

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_coordinate = int((screen_width/2) - (window_width/2))
y_coordinate = int((screen_height/2) - (window_height/2))

root.geometry('{}x{}+{}+{}'.format(window_width, window_height, x_coordinate, y_coordinate))

# root.geometry('500x500') # use this if above doesnt work
root.pack_propagate(False)

# GUI variables
col_options_list = ['Columns'] # this will be the columns from input csv
var_col_choice = StringVar()
var_col_choice.set(col_options_list[0])

# Used in session_analysis_page and sector_analysis_page
normalize_stationary_bool = BooleanVar(value=False)
rmv_stationary_bool = BooleanVar(value=False)

# Used in limp_mode_page
spinbox_max_temp_diff_from_avg = IntVar(value=c.MAX_TEMP_DIFF_FROM_AVG)


def clear_page():
    for widget in root.winfo_children():
        widget.destroy()


def main_btn():
    button_main = Button(root, text=' Main Menu ', command=lambda: main_menu_page())
    button_main.place(x=0, y=0)

    return None


def main_menu_page():
    clear_page()
    main_btn()
    
    # temp
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=3)
    root.grid_rowconfigure(2, weight=3)
    root.grid_rowconfigure(3, weight=3)

    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=2)
    root.grid_columnconfigure(2, weight=1)
    # temp

    ## Frame for file dialog
    frame_main = LabelFrame(root, text='', font=18, bd=2, relief='ridge')
    frame_main.place(height=300, width=400, rely=0.5, relx=.5, y=-50, anchor=CENTER)

    page_title = Label(root, text='UConn FSAE DAQ Multitool')
    page_title.place(relx=.5, y=37, anchor=CENTER)
    page_title.config(font=('arial', 20))
    
    label1 = Label(frame_main, text='Select an analysis method.')
    label1.place(rely=.15, relx=.5, anchor=CENTER)

    label2 = Label(frame_main, text=
                   '*Lorem ipsum'
                   ,justify=LEFT, wraplength=800)
    label2.place(rely=.91, relx=.5, anchor=CENTER)
    

    ## Buttons
    button1 = Button(frame_main, text='Basic Stats', command=lambda: basic_stats_page())
    button1.place(rely=0.35, relx=.40, x=-5, width=80, anchor=CENTER)

    button2 = Button(frame_main, text='Sector Analysis', command=lambda: sector_analysis_page())
    button2.place(rely=0.35, relx=0.60, x=5, width=80, anchor=CENTER)

    button3 = Button(frame_main, text='Coastdown Analysis', command=lambda: coast_down_page())
    button3.place(rely=0.50, relx=0.50, width=165, anchor=CENTER)

    button4 = Button(frame_main, text='Limp Mode Analysis', command=lambda: limp_mode_page())
    button4.place(rely=0.65, relx=0.50, width=165, anchor=CENTER)

## Main Menu Page End


def display_csv(treeview, df):
    ## Code to display dataframe in tree-view
    treeview['columns'] = list(df.columns) # ex) data['attribute']
    treeview['show'] = 'headings'
    for column in treeview['columns']:
        treeview.heading(column, text=column)
    
    df_rows = df.to_numpy().tolist()
    for row in df_rows: # for each row in df, insert into tree view
        treeview.insert('', 'end', values=row)

    list_headers = df.columns.values.tolist()
    for column in list_headers:
        treeview.column(column, width=10, stretch=YES)

    return None


def clear_treeview(trees: list, lables: list):
    # print(type(trees))
    for treeview in trees:
        treeview.delete(*treeview.get_children())
        treeview['columns'] = [None]
    
    if lables is None:
        return None
    else:
        for label in lables:
            label['text'] = label['text'].split(':')[0] + ':'

    return None


def select_file(treeview: list, file_label):
    # Used for generic files without necessary formatting (sectors.csv)
    global df_file

    clear_treeview([treeview], [file_label])

    file = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                        ('All Files', '*.*')))
    if file == '' or file is None:
        return None

    df_file = pd.read_csv(file, encoding='ISO-8859-1').reset_index(drop=True)

    display_csv(treeview, df_file)

    return None


def select_file_v2(treeview: list, file_label):
    # used to select datafiles from racestudio
    ## ** is there another way to use the df_data instead of makeing it global?
    global df_reference_file

    clear_treeview([treeview], [file_label]) # lists so we can clear multple objects

    file = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                        ('All Files', '*.*')))
    if file == '' or file is None:
        return None

    df_reference_file = pd.read_csv(file, encoding='ISO-8859-1').reset_index(drop=True)

    leading_label = file_label['text'].split(':')[0] + ':'
    file_label['text'] = f'{leading_label} {file}'

    display_csv(treeview, df_reference_file)

    return None


def select_datafile1(treeview: list, file_label):
    # used to select datafiles from racestudio
    ## ** is there another way to use the df_data instead of makeing it global?
    global df_aim_data1

    clear_treeview([treeview], [file_label]) # lists so we can clear multple objects

    file = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                        ('All Files', '*.*')))
    if file == '' or file is None:
        return None
    # else:
    #     pass
        # file_data.delete(*file_data.get_children()) # unpack all rows

    df_input = pd.read_fwf(file, header=None, encoding='ISO-8859-1').reset_index(drop=True)

    leading_label = file_label['text'].split(':')[0] + ':'
    file_label['text'] = f'{leading_label} {file}'

    df_aim_data1 = format_data(df_input)

    display_csv(treeview, df_aim_data1)

    # ** fix/convert to function later
    # if is_col_choice:
    try:
        # update_col_option_menu()
        # https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
        # Answer from: user2555451
        optionmenu_var_col['menu'].delete(0, 'end')

        # Insert list of new options (tk._setit hooks them up to var)
        new_cols = df_aim_data1.columns
        for col in new_cols:
            optionmenu_var_col['menu'].add_command(label=col, command=tk._setit(var_col_choice, col))

        var_col_choice.set(new_cols[-1])
        # print('Updated Option Menu')
        # print(var_col_choice.get())
    except:
        pass

    return None


def select_datafile2(treeview: list, file_label):
    # used to select datafiles from racestudio
    ## ** is there another way to use the df_data instead of makeing it global?
    global df_aim_data2

    clear_treeview([treeview], [file_label]) # lists so we can clear multple objects

    file = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                        ('All Files', '*.*')))
    if file == '' or file is None:
        return None
    # else:
    #     pass
        # file_data.delete(*file_data.get_children()) # unpack all rows

    df_input = pd.read_fwf(file, header=None, encoding='ISO-8859-1').reset_index(drop=True)

    leading_label = file_label['text'].split(':')[0] + ':'
    file_label['text'] = f'{leading_label} {file}'

    df_aim_data2 = format_data(df_input)

    display_csv(treeview, df_aim_data2)

    # ** fix/convert to function later
    # if is_col_choice:
    try:
        # update_col_option_menu()
        # https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
        # Answer from: user2555451
        optionmenu_var_col['menu'].delete(0, 'end')

        # Insert list of new options (tk._setit hooks them up to var)
        new_cols = df_aim_data2.columns
        for col in new_cols:
            optionmenu_var_col['menu'].add_command(label=col, command=tk._setit(var_col_choice, col))

        var_col_choice.set(new_cols[-1])
        # print('Updated Option Menu')
        # print(var_col_choice.get())
    except:
        pass


    return None


def export_df_to_csv(df, output_location):
    df.to_csv(output_location, index=False)


def create_window(window_name):
    graph_window = tk.Toplevel(root)
    graph_window.wm_title(window_name)
    
    # plot_test2(graph_window)
    # graph_window.mainloop() # Not needed for sub windows.

    return graph_window

    
def create_plot_test():
    # fig = plt.Figure(figsize=(8, 4), dpi=100)
    fig = plt.Figure(figsize=(8, 4.5), dpi=200, layout='tight')
    t = np.arange(0, 3, .01)
    ax = fig.add_subplot()
    line, = ax.plot(t, 2 * np.sin(2 * np.pi * t))
    ax.set_xlabel("time [s]")
    ax.set_ylabel("f(t)")

    return fig

    
def plot_test3(windows_list: list):
    fig = create_plot_test()
    # pack_toolbar=False will make it easier to use a layout manager later on.
    for window in windows_list:
        canvas = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, window, pack_toolbar=True)
        toolbar.update()

        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        toolbar.pack(side=BOTTOM, fill=X)

    return None

    
def popup_graph(plot, subwindow):
    canvas = FigureCanvasTkAgg(plot, master=subwindow)  # A tk.DrawingArea.
    canvas.draw()
    # pack_toolbar=False will make it easier to use a layout manager later on.
    toolbar = NavigationToolbar2Tk(canvas, subwindow, pack_toolbar=True)
    toolbar.update()

    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
    toolbar.pack(side=BOTTOM, fill=X)

    return None


def plot_test2(window):
    fig = create_plot_test()

    canvas = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
    canvas.draw()
    
    # pack_toolbar=False will make it easier to use a layout manager later on.
    toolbar = NavigationToolbar2Tk(canvas, window, pack_toolbar=False)
    toolbar.update()

    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
    toolbar.pack(side=BOTTOM, fill=X)

    return None


def plot_test(frame):
    fig = create_plot_test()

    canvas = FigureCanvasTkAgg(figure=fig, master=root)  # A tk.DrawingArea.
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()

    canvas.get_tk_widget().grid(row=0, rowspan=1, column=1)

    return None


def create_treeview(frame):
    tree_data = ttk.Treeview(frame)
    tree_data.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(tree_data, orient='vertical', command=tree_data.yview)
    treescrollx = Scrollbar(tree_data, orient='horizontal', command=tree_data.xview)
    tree_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')  

    return tree_data


def basic_stats_page():
    global optionmenu_var_col

    clear_page()
    # main_btn() 
    # ** either make main_btn() work with the grid; make this so its always 
    # ontop; or place at bottom of function (it will be placed last, thus on top)

    ## ** reformat grid
    ## Grid configuration # ... how to reset grid... this doesnt change the previous configuration 
    # root.grid_rowconfigure(0, weight=1)
    # root.grid_rowconfigure(1, weight=3)
    # root.grid_rowconfigure(2, weight=3)

    # root.grid_columnconfigure(0, weight=2)
    # root.grid_columnconfigure(1, weight=2)

    ## Page layout
    header_frame = LabelFrame(root, bd=1, relief='flat')
    treeview1_frame = LabelFrame(root, text='Session Data', font=14, bd=2, relief='ridge')
    treeview2_frame = LabelFrame(root, text='Session Analysis', font=14, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=14, bd=2, relief='ridge')
    info_frame = LabelFrame(root, text='Info', font=14, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    treeview1_frame.grid(row=1, rowspan=2, column=0, columnspan=1, sticky='nsew', padx=2, pady=2)
    treeview2_frame.grid(row=1, rowspan=2, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
    info_frame.grid(row=3, column=1, columnspan=3, sticky='nsew', padx=2, pady=2)
    ## Grid End
    
    # Widgets

    # Page title
    page_title = Label(header_frame, text='UConn FSAE DAQ Multitool')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 14))
    
    ## Treeview 1 widget
    tree1_data = create_treeview(treeview1_frame)

    ## Treeview 2 widget
    tree2_data = create_treeview(treeview2_frame)
    
    ## Main Buttons
    button1 = Button(button_frame, text='Data File', command=lambda: select_datafile1(tree1_data, filepath_label1))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data, tree2_data], [filepath_label1]))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    # button3 = Button(button_frame, text='Process Data', command=lambda: session_analysis(df_data, var_col_choice))
    button3 = Button(button_frame, text='Process Data', command=lambda: output_session_analysis(basic_stats(df_aim_data1, var_col_choice.get(), normalize_stationary_bool.get(), rmv_stationary_bool.get()), tree2_data))
    button3.place(y=30, relx=.75, width=80, anchor=CENTER)

    # test
    export_button = Button(tree2_data, text='Export Data', command=lambda: export_df_to_csv(df_sector_analysis, c.sector_analysis_path))
    export_button.pack(anchor='se', side='bottom')
    # test

    ## Options
    # col_options_list; this list variable could update when a file is inputed and filled in with available columns
    optionmenu_var_col = OptionMenu(button_frame, var_col_choice, *col_options_list, command=lambda x: print(f'OptionMenu: {x}'))
    optionmenu_var_col.place(y=70, relx=.75, anchor=CENTER)

    checkbox_normalize = Checkbutton(button_frame, text='Normalize stationary Values (description)', 
                            variable=normalize_stationary_bool, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_normalize.place(y=122, relx=.5, anchor=CENTER)

    checkbox_rmv_stationary = Checkbutton(button_frame, text='Remove stationary values (description)    ', 
                            variable=rmv_stationary_bool, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_rmv_stationary.place(y=142, relx=.5, anchor=CENTER)

    ## Statistics
    filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(info_frame, text='''
                                    Mandatory columns:\n
                                    Time, Distance
                                    '''
                                    , wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(info_frame, text='Time, Distance', wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    # stat4_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    # stat4_label.place(y=135, x=10)
    
    main_btn()

    return None


def sector_analysis_page():
    global optionmenu_var_col

    clear_page()
    # main_btn() 
    # ** either make main_btn() work with the grid; make this so its always 
    # ontop; or place at bottom of function (it will be placed last, thus on top)

    ## Grid configuration
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=3)
    root.grid_rowconfigure(2, weight=3)
    root.grid_rowconfigure(3, weight=3)

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=2)

    ## Page layout
    header_frame = LabelFrame(root, bd=1, relief='flat')
    treeview1_frame = LabelFrame(root, text='Session Data', font=14, bd=2, relief='ridge')
    treeview2_frame = LabelFrame(root, text='Sectors', font=14, bd=2, relief='ridge')
    treeview3_frame = LabelFrame(root, text='Analysis', font=14, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=14, bd=2, relief='ridge')
    info_frame = LabelFrame(root, text='Info', font=14, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
    treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
    treeview3_frame.grid(row=1, rowspan=2, column=2, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
    info_frame.grid(row=3, column=2, columnspan=2, sticky='nsew', padx=2, pady=2)
    
    # Widgets
    page_title = Label(header_frame, text='UConn FSAE DAQ Multitool')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 14))
    
    ## Treeview 1 widget ## ** create function
    tree1_data = create_treeview(treeview1_frame)
    
    ## Treeview 2 widget
    tree2_data = create_treeview(treeview2_frame)
    
    ## Treeview 3 widget
    tree3_data = create_treeview(treeview3_frame)
    
    ## Main Buttons
    button1 = Button(button_frame, text='Data File', command=lambda: select_datafile1(tree1_data, filepath_label1))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Sectors File', command=lambda: select_file_v2(tree2_data, filepath_label2))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data, tree2_data, tree3_data], [filepath_label1, filepath_label2]))
    button3.place(y=30, relx=.75, width=80, anchor=CENTER)
    # **
    button4 = Button(button_frame, text='Process Data', command=lambda: output_sector_analysis(
        init_sector_analysis(df_aim_data1, df_reference_file, var_col_choice.get(), normalize_stationary_bool.get(), rmv_stationary_bool.get()),
        tree3_data)
        )
    button4.place(y=70, relx=.75, width=80, anchor=CENTER)
    
    export_button = Button(treeview3_frame, text='Export Data', command=lambda: export_df_to_csv(df_sector_analysis, c.sector_analysis_path))
    export_button.pack(padx=15, pady=15, anchor='se', side='bottom')

    ## Options
    optionmenu_var_col = OptionMenu(button_frame, var_col_choice, *col_options_list, command=lambda x: print(f'OptionMenu: {x}'))
    optionmenu_var_col.place(y=110, relx=.25, anchor=CENTER)

    checkbox_normalize = Checkbutton(button_frame, text='Normalize stationary\nvalues (description)', 
                            variable=normalize_stationary_bool, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_normalize.place(y=110, relx=.75, anchor=CENTER)

    checkbox_rmv_stationary = Checkbutton(button_frame, text='Remove stationary\nvalues (description)    ', 
                            variable=rmv_stationary_bool, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_rmv_stationary.place(y=150, relx=.75, anchor=CENTER)

    ## Statistics
    filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    filepath_label2 = Label(info_frame, text='File 2: ', wraplength=450, justify=LEFT)
    filepath_label2.place(y=55, x=10)

    stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(info_frame, text='Mandatory columns: ', wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(info_frame, text='Time, Distance ', wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    # stat4_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    # stat4_label.place(y=135, x=10)

    main_btn()

    return None


def coast_down_page():
    clear_page()
    # main_btn() 
    # ** either make main_btn() work with the grid; make this so its always 
    # ontop; or place at bottom of function (it will be placed last, thus on top)

    ## Grid configuration # ... how to reset grid... this doesnt change the previous configuration 
    # root.grid_rowconfigure(0, weight=1)
    # root.grid_rowconfigure(1, weight=3)
    # root.grid_rowconfigure(2, weight=3)

    # root.grid_columnconfigure(0, weight=2)
    # root.grid_columnconfigure(1, weight=2)

    # temp
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=3)
    root.grid_rowconfigure(2, weight=3)
    root.grid_rowconfigure(3, weight=3)

    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=2)
    root.grid_columnconfigure(2, weight=1)
    # temp


    ## Page layout
    header_frame = LabelFrame(root, bd=1, relief='flat')
    treeview1_frame = LabelFrame(root, text='Coastdown Data', font=14, bd=2, relief='ridge')
    plot1_frame = LabelFrame(root, text='Downforce vs Speed', font=14, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=14, bd=2, relief='ridge')
    info_frame = LabelFrame(root, text='Info', font=14, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    treeview1_frame.grid(row=1, rowspan=2, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
    plot1_frame.grid(row=1, rowspan=2, column=2, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
    info_frame.grid(row=3, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
    ## Grid End
    
    # Widgets

    page_title = Label(header_frame, text='UConn FSAE DAQ Multitool')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 14))
    
    ## Treeview 1 widget
    tree1_data = ttk.Treeview(treeview1_frame)
    tree1_data.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(tree1_data, orient='vertical', command=tree1_data.yview)
    treescrollx = Scrollbar(tree1_data, orient='horizontal', command=tree1_data.xview)
    tree1_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')    
    
    ## Main Buttons
    button1 = Button(button_frame, text='Data File', command=lambda: select_datafile1(tree1_data, filepath_label1))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data], [filepath_label1]))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Process Data', command=lambda: popup_graph(
        init_downforce_analysis(df_aim_data1),
        create_window('Downforce vs Speed')))
    button3.place(y=70, relx=.75, width=80, anchor=CENTER)
    
    ## Statistics
    filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(info_frame, text='Mandatory columns:', wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(info_frame, text='Time, Distance, YawRate, Front_Left_Forc, Front_Right_Forc, Rear_Right_Force, Rear_Left_Force, S8_tps1, F_Brake_Press, R_Brake_Pres, GPS_Speed',
        wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    # stat4_label = Label(info_frame, text='...', wraplength=350, justify=LEFT)
    # stat4_label.place(y=135, x=10)
    
    # Graph Buttons
    # graph_button1 = Button(plot1_frame, text='Graph', command=lambda: False)
    # graph_button1.place(rely=.5, relx=.5, width=80, anchor=CENTER)

    main_btn()

    return None


def limp_mode_page():
    clear_page()
    # main_btn() 
    # ** either make main_btn() work with the grid; make this so its always 
    # ontop; or place at bottom of function (it will be placed last, thus on top)

    ## Grid configuration
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=3)
    root.grid_rowconfigure(2, weight=3)
    root.grid_rowconfigure(3, weight=3)

    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=2)
    root.grid_columnconfigure(2, weight=1)

    ## Page layout
    header_frame = LabelFrame(root, bd=1, relief='flat')
    treeview1_frame = LabelFrame(root, text='100% Oil', font=14, bd=2, relief='ridge')
    treeview2_frame = LabelFrame(root, text='x% Oil', font=14, bd=2, relief='ridge')
    plot1_frame = LabelFrame(root, text='Coolant Temp vs Time', font=14, bd=2, relief='ridge')
    plot2_frame = LabelFrame(root, text='Coolant Temp vs RPM', font=14, bd=2, relief='ridge')
    plot3_frame = LabelFrame(root, text='RPM % Change', font=14, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=14, bd=2, relief='ridge')
    info_frame = LabelFrame(root, text='Info', font=14, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
    treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
    plot1_frame.grid(row=1, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    plot2_frame.grid(row=2, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    plot3_frame.grid(row=3, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
    info_frame.grid(row=3, column=1, columnspan=1, sticky='nsew', padx=2, pady=2)
    
    # Widgets
    page_title = Label(header_frame, text='UConn FSAE DAQ Multitool')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 14))
    
    ## Treeview 1 widget
    tree1_data = ttk.Treeview(treeview1_frame)
    tree1_data.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(tree1_data, orient='vertical', command=tree1_data.yview)
    treescrollx = Scrollbar(tree1_data, orient='horizontal', command=tree1_data.xview)
    tree1_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')    
    
    ## Treeview 2 widget
    tree2_data = ttk.Treeview(treeview2_frame)
    tree2_data.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(tree2_data, orient='vertical', command=tree2_data.yview)
    treescrollx = Scrollbar(tree2_data, orient='horizontal', command=tree2_data.xview)
    tree2_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')    
    
    ## Main Buttons
    button1 = Button(button_frame, text='Oil File 1', command=lambda: select_datafile1(tree1_data, filepath_label1))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Oil File 2', command=lambda: select_datafile2(tree2_data, filepath_label2))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data, tree2_data], [filepath_label1, filepath_label2]))
    button3.place(y=30, relx=.75, width=80, anchor=CENTER)

    # button4 = Button(button_frame, text='Process Data', command=lambda: plot_test3([plot1_frame, plot2_frame, plot3_frame]))
    button4 = Button(button_frame, text='Process Data', command=lambda: init_oil_analysis([df_aim_data1, df_aim_data2], int(spinbox_max_temp_diff_from_avg.get()))) # ** displays all graphs at once.
    button4.place(y=70, relx=.75, width=80, anchor=CENTER)

    spinbox1 = Spinbox(button_frame, from_=0, to=99, textvariable=spinbox_max_temp_diff_from_avg)
    spinbox1.place(y=140, relx=.25, width=80, anchor=CENTER)
    spinbox1_label = Label(button_frame, text='Max temperature difference from\naverage (used to remove outliers)')
    spinbox1_label.place(relx=.25, y=110, anchor=CENTER)

    ## Statistics
    filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    filepath_label2 = Label(info_frame, text='File 2: ', wraplength=450, justify=LEFT)
    filepath_label2.place(y=55, x=10)

    stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(info_frame, text='Mandatory columns:', wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(info_frame, text='Time, Distance, S8_RPM, S*eot, S8_ect1, S8_eop', wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    # stat4_label = Label(info_frame, text='... ', wraplength=350, justify=LEFT)
    # stat4_label.place(y=135, x=10)
    
    # Graph Buttons
    # graph_button1 = Button(plot1_frame, text='Graph 1', command=lambda: create_window(graph_button1['text']))
    # graph_button1.place(rely=.5, relx=.5, width=80, anchor=CENTER)

    # graph_button2 = Button(plot2_frame, text='Graph 2', command=lambda: create_window(graph_button2['text']))
    # graph_button2.place(rely=.5, relx=.5, width=80, anchor=CENTER)

    # graph_button3 = Button(plot3_frame, text='Graph 3', command=lambda: create_window(graph_button3['text']))
    # graph_button3.place(rely=.5, relx=.5, width=80, anchor=CENTER)
    
    main_btn()

    return None


def output_session_analysis(df, treeview):
    # helpfer function to get dataframe from session_analysis and display to GUI
    clear_treeview([treeview], None)
    display_csv(treeview, df)

    return df


def output_sector_analysis(df, treeview):
    # helper function to get dataframe from session_analysis and display to GUI
    global df_sector_analysis
    
    clear_treeview([treeview], None)
    df_sector_analysis = df

    df_sector_analysis['Stats'] = c.SECTOR_STATS_LABELS

    first_column = df_sector_analysis.pop('Stats')
    df_sector_analysis.insert(0, 'Stats', first_column)

    display_csv(treeview, df_sector_analysis)

    return df_sector_analysis


def output_downforce_graph(plot, treeview):
    # helper function to get dataframe from session_analysis and display to GUI
    # df = df.to_frame()
    # ** create constant for the list below\


    return None


def main():
    main_menu_page()

    return None


main()
root.mainloop()
