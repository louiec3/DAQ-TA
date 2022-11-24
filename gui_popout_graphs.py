####################################################################
# UConn Formula SAE
# Data Acquisition - Multifunction Analysis Tool
# Date Uploaded: __/__/____
# A tool to automate data analysis for the UConn FSAE team.
# Louis Cundari III
# louis.cundari@uconn.edu | louiscundari3@outlook.com
####################################################################

## Note
# Look into storing text in a txt file and references that text
# ie an about page could contain a paragraph and not be needed in the code itself
## Note end


import tkinter as tk
from tkinter import * # remove * and add used functions later
from tkinter import ttk, filedialog, messagebox, simpledialog
from os.path import dirname, abspath 
import os
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np

root = Tk()

root.title('Multifunction Staistics Tool')
root.state('zoomed')

window_height = 600
window_width = 700

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_coordinate = int((screen_width/2) - (window_width/2))
y_coordinate = int((screen_height/2) - (window_height/2))

root.geometry('{}x{}+{}+{}'.format(window_width, window_height, x_coordinate, y_coordinate))

# root.geometry('500x500') # use this if above doesnt work
root.pack_propagate(False)


def clear_page():
    for widget in root.winfo_children():
        widget.destroy()


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

    button3 = Button(frame_main, text='Coastdown Analysis', command=lambda: coastdown_page())
    button3.place(rely=0.50, relx=0.50, width=165, anchor=CENTER)

    button4 = Button(frame_main, text='Limp Mode Analysis', command=lambda: limp_mode_page())
    button4.place(rely=0.65, relx=0.50, width=165, anchor=CENTER)

## Main Menu Page End


def main_btn():
    # temp
    # root.grid_rowconfigure(0, weight=1)
    # root.grid_rowconfigure(1, weight=3)
    # root.grid_rowconfigure(2, weight=3)
    # root.grid_rowconfigure(3, weight=3)

    # root.grid_columnconfigure(0, weight=2)
    # root.grid_columnconfigure(1, weight=2)
    # root.grid_columnconfigure(2, weight=1)
    # temp


    button_main = Button(root, text=' Main Menu ', command=lambda: main_menu_page())
    button_main.place(x=0, y=0)

    return None


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
    
    for label in lables:
        label['text'] = label['text'].split(':')[0] + ':'

    return None


# ** why do we need [treeview] and [file_label]? Linked to clear_treeview
# Insert a good ol', "I dont know why it works, but it does" (refering to the [treeview] and why it needs [])
def select_file_window(treeview: list, file_label):
    clear_treeview([treeview], [file_label])

    file = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                        ('All Files', '*.*')))
    if file == '' or file is None:
        return None
    else:
        pass
        # file_data.delete(*file_data.get_children()) # unpack all rows

    df_input = pd.read_fwf(file, header=None, encoding='ISO-8859-1').reset_index(drop=True)

    leading_label = file_label['text'].split(':')[0] + ':'
    file_label['text'] = f'{leading_label} {file}'

    # ** Create function to import dataframe into treeview
    display_csv(treeview, df_input)

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
    button1 = Button(button_frame, text='Oil File 1', command=lambda: select_file_window(tree1_data, filepath_label1))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Oil File 2', command=lambda: select_file_window(tree2_data, filepath_label2))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data, tree2_data], [filepath_label1, filepath_label2]))
    button3.place(y=30, relx=.75, width=80, anchor=CENTER)

    button4 = Button(button_frame, text='Process Data', command=lambda:plot_test3([plot1_frame, plot2_frame, plot3_frame]))
    button4.place(y=70, relx=.75, width=80, anchor=CENTER)
    
    ## Statistics
    filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    filepath_label2 = Label(info_frame, text='File 2: ', wraplength=450, justify=LEFT)
    filepath_label2.place(y=55, x=10)

    stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    stat4_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat4_label.place(y=135, x=10)
    
    # Graph Buttons
    graph_button1 = Button(plot1_frame, text='Graph 1', command=lambda: create_window(graph_button1['text']))
    graph_button1.place(rely=.5, relx=.5, width=80, anchor=CENTER)

    graph_button2 = Button(plot2_frame, text='Graph 2', command=lambda: create_window(graph_button2['text']))
    graph_button2.place(rely=.5, relx=.5, width=80, anchor=CENTER)

    graph_button3 = Button(plot3_frame, text='Graph 3', command=lambda: create_window(graph_button3['text']))
    graph_button3.place(rely=.5, relx=.5, width=80, anchor=CENTER)
    
    main_btn()

    return None


def create_window(window_name):
    subwindow = tk.Toplevel(root)
    subwindow.wm_title(window_name)
    
    plot_test2(subwindow)

    subwindow.mainloop() # works without this line...?

    return None

    
def create_plot_test():
    # fig = plt.Figure(figsize=(8, 4), dpi=100)
    fig = plt.Figure(figsize=(5.3, 3), dpi=100, layout='tight')
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


def plot_test2(window):
    fig = create_plot_test()
    # pack_toolbar=False will make it easier to use a layout manager later on.
    
    canvas = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, window, pack_toolbar=False)
    toolbar.update()

    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
    toolbar.pack(side=BOTTOM, fill=X)

    return None


def plot_test(frame):
    fig = create_plot_test()

    canvas = FigureCanvasTkAgg(figure=fig, master=root)  # A tk.DrawingArea.
    canvas.draw()

    # pack_toolbar=False will make it easier to use a layout manager later on.
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()

    # button_quit = tk.Button(master=frame, text="Quit", command=root.destroy)


    # slider_update = tk.Scale(frame, from_=1, to=5, orient=tk.HORIZONTAL,
    #                             command=False, label="Frequency [Hz]")

    # Packing order is important. Widgets are processed sequentially and if there
    # is no space left, because the window is too small, they are not displayed.
    # The canvas is rather flexible in its size, so we pack it last which makes
    # sure the UI controls are displayed as long as possible.
    # button_quit.pack(side=tk.BOTTOM)
    # slider_update.pack(side=tk.BOTTOM)
    
    # toolbar.pack(side=tk.BOTTOM, fill=tk.X)
    # toolbar.grid(row=4, column=2, sticky='nsew', padx=2, pady=2)

    # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    # canvas.get_tk_widget().grid(row=0, rowspan=3, column=0, columnspan=4, sticky='nsew', padx=2, pady=2)
    canvas.get_tk_widget().grid(row=0, rowspan=1, column=1)

    # canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=2, pady=2)

    return None


def coastdown_page():
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
    plot1_frame = LabelFrame(root, text='Downforce Plot', font=14, bd=2, relief='ridge')
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
    button1 = Button(button_frame, text='Data File', command=lambda: select_file_window(tree1_data, filepath_label1))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data], [filepath_label1]))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Process Data', command=lambda:plot_test3([plot1_frame]))
    button3.place(y=70, relx=.75, width=80, anchor=CENTER)
    
    ## Statistics
    filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    stat4_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat4_label.place(y=135, x=10)
    
    # Graph Buttons
    graph_button1 = Button(plot1_frame, text='Graph 1', command=lambda: create_window(graph_button1['text']))
    graph_button1.place(rely=.5, relx=.5, width=80, anchor=CENTER)

    main_btn()

    return None
    

def basic_stats_page():
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
    treeview2_frame = LabelFrame(root, text='Basic Analysis', font=14, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=14, bd=2, relief='ridge')
    info_frame = LabelFrame(root, text='Info', font=14, bd=2, relief='ridge')

    header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    treeview1_frame.grid(row=1, rowspan=2, column=0, columnspan=1, sticky='nsew', padx=2, pady=2)
    treeview2_frame.grid(row=1, rowspan=2, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
    button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
    info_frame.grid(row=3, column=1, columnspan=3, sticky='nsew', padx=2, pady=2)
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
    
    ## Treeview 2 widget
    tree2_data = ttk.Treeview(treeview2_frame)
    tree2_data.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(tree2_data, orient='vertical', command=tree2_data.yview)
    treescrollx = Scrollbar(tree2_data, orient='horizontal', command=tree2_data.xview)
    tree2_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')    
    
    ## Main Buttons
    button1 = Button(button_frame, text='Data File', command=lambda: select_file_window(tree1_data, filepath_label1))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data], [filepath_label1]))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Process Data', command=lambda: False)
    button3.place(y=30, relx=.75, width=80, anchor=CENTER)

    # ** Needs work
    param_options_list = ['Col 1', 'Col 2', 'Col 3'] # this will be the columns from input csv
    var = StringVar()
    var.set(param_options_list[0])
    # parm_options_list this list variable could update when a file is inputed and filled in with available columns
    optionmenu_format1 = OptionMenu(button_frame, var, *param_options_list, command=lambda x: print(f'OptionMenu: {x}'))
    optionmenu_format1.place(y=70, relx=.75, anchor=CENTER)

    var1_temp = IntVar(value=1)
    var2_temp = IntVar(value=1)
    checkbox_normalize = Checkbutton(button_frame, text='Normalize stationary Values (description)', 
                            variable=var1_temp, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_normalize.place(y=122, relx=.5, anchor=CENTER)

    checkbox_remove_stationary = Checkbutton(button_frame, text='Remove stationary values (description)    ', 
                            variable=var2_temp, onvalue=1, offvalue=0, justify=LEFT)
    checkbox_remove_stationary.place(y=142, relx=.5, anchor=CENTER)

    ## Statistics
    filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    stat4_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat4_label.place(y=135, x=10)
    
    main_btn()

    return None


def sector_analysis_page():
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
    button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
    info_frame.grid(row=3, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
    
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
    button1 = Button(button_frame, text='Data File', command=lambda: select_file_window(tree1_data, filepath_label1))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Sectors File', command=lambda: select_file_window(tree2_data, filepath_label2))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data, tree2_data], [filepath_label1, filepath_label2]))
    button3.place(y=30, relx=.75, width=80, anchor=CENTER)

    button4 = Button(button_frame, text='Process Data', command=lambda: False)
    button4.place(y=70, relx=.75, width=80, anchor=CENTER)
    
    ## Statistics
    filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    filepath_label2 = Label(info_frame, text='File 2: ', wraplength=450, justify=LEFT)
    filepath_label2.place(y=55, x=10)

    stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    stat4_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    stat4_label.place(y=135, x=10)
    

    main_btn()

    return None


def main():
    main_menu_page()
    # limp_mode_page()

    return None

main()
root.mainloop()
