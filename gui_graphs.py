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


def clear_treeview(trees):
    for treeview in trees:
        treeview.delete(*treeview.get_children())

    return None


def file_select_window(treeview: list, file_label, file_label_text):
    clear_treeview([treeview])

    file = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                        ('All Files', '*.*')))
    if file == '' or file is None:
        return None
    else:
        pass
        # file_data.delete(*file_data.get_children()) # unpack all rows

    # if os.path.splitext(file)[1] == '.csv':
        # import_filename = r'{}'.format(file)
    df_input = pd.read_fwf(file, header=None, encoding='ISO-8859-1').reset_index(drop=True)

    file_label['text'] = f'{file_label_text} {file}'

    # ** Create function to import dataframe into treeview
    display_csv(treeview, df_input)

    return None


def limp_mode_page():
    ## Grid configuration
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)

    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=2)
    root.grid_columnconfigure(2, weight=3)


    ## Page layout
    header_frame = LabelFrame(root, bd=1, relief='flat')
    treeview1_frame = LabelFrame(root, text='100% Oil', font=14, bd=2, relief='ridge')
    treeview2_frame = LabelFrame(root, text='X% Oil', font=14, bd=2, relief='ridge')
    plot1_frame = LabelFrame(root, text='Plot 1', font=14, bd=2, relief='ridge')
    plot2_frame = LabelFrame(root, text='Plot 2', font=14, bd=2, relief='ridge')
    plot3_frame = LabelFrame(root, text='Plot 3', font=14, bd=2, relief='ridge')
    button_frame = LabelFrame(root, text='Options', font=14, bd=2, relief='ridge')
    summary_frame = LabelFrame(root, text='Summary', font=14, bd=2, relief='ridge')

    treeview1_frame.grid(row=0, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
    treeview2_frame.grid(row=0, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
    plot1_frame.grid(row=0, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    plot2_frame.grid(row=1, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    plot3_frame.grid(row=2, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    
    
    button_frame.grid(row=2, column=0, sticky='nsew', padx=2, pady=2)
    summary_frame.grid(row=2, column=1, columnspan=1, sticky='nsew', padx=2, pady=2)
    ## Grid End
    
    # Widgets

    page_title = Label(header_frame, text='EWR Builder: Import a File')
    page_title.place(relx=.5, rely=.5, anchor=CENTER)
    page_title.config(font=('arial', 14))
    
    ## Treeview 2 widget
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
    
    ## Buttons
    button1 = Button(button_frame, text='Initial Oil', command=lambda: file_select_window(tree1_data, filepath_label1, 'File 1:'))
    button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Compare Oil', command=lambda: file_select_window(tree2_data, filepath_label2, 'File 2:'))
    button2.place(y=30, relx=.75, width=80, anchor=CENTER)

    button2 = Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data, tree2_data]))
    button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    button3 = Button(button_frame, text='Process Data', command=lambda: plot_test2(plot1_frame))
    button3.place(y=70, relx=.75, width=80, anchor=CENTER)

    ## Statistics
    filepath_label1 = Label(summary_frame, text='File 1: ', wraplength=450, justify=LEFT)
    filepath_label1.place(y=10, x=10)

    filepath_label2 = Label(summary_frame, text='File 2: ', wraplength=450, justify=LEFT)
    filepath_label2.place(y=55, x=10)

    stat1_label = Label(summary_frame, text=' ', wraplength=350, justify=LEFT)
    stat1_label.place(y=75, x=10)

    stat2_label = Label(summary_frame, text='Text ', wraplength=350, justify=LEFT)
    stat2_label.place(y=95, x=10)

    stat3_label = Label(summary_frame, text='Text ', wraplength=350, justify=LEFT)
    stat3_label.place(y=115, x=10)
    
    stat4_label = Label(summary_frame, text='Text ', wraplength=350, justify=LEFT)
    stat4_label.place(y=135, x=10)
    
    
def create_plot_test():
    # fig = plt.Figure(figsize=(8, 4), dpi=100)
    fig = plt.Figure(figsize=(5,2), dpi=100, layout='tight')
    t = np.arange(0, 3, .01)
    ax = fig.add_subplot()
    line, = ax.plot(t, 2 * np.sin(2 * np.pi * t))
    ax.set_xlabel('time (s)')
    ax.set_ylabel('f(t)')

    return fig

    
def plot_test2(frame):
    fig = create_plot_test()
    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=0, rowspan=1, column=2, columnspan=3)
    canvas.draw()
    
    # pack_toolbar=False will make it easier to use a layout manager later on.
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()
    toolbar.grid(row=0, column=2, sticky='s')

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=1, rowspan=1, column=2, columnspan=3)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()
    toolbar.grid(row=1, column=2, sticky='s')
    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=2, rowspan=1, column=2, columnspan=3)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()
    toolbar.grid(row=2, column=2, sticky='s')


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


def main():
    limp_mode_page()


main()
root.mainloop()
