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


def main_btn():
    button_main = Button(root, text=' Main Menu ', command=lambda: False)
    button_main.place(x=0, y=0)

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


def limp_mode_page():
    clear_page()
    # main_btn() 
    # ** either make main_btn() work with the grid; make this so its always 
    # ontop; or place at bottom of function (it will be placed last, thus on top)

    ## Grid configuration
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_rowconfigure(4, weight=1)
    # root.grid_rowconfigure(5, weight=1)

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    # root.grid_columnconfigure(3, weight=1)
    # root.grid_columnconfigure(4, weight=1)
    # root.grid_columnconfigure(5, weight=1)

    test1_frame = LabelFrame(root, text='1', font=14, bd=2, relief='ridge')
    test2_frame = LabelFrame(root, text='2', font=14, bd=2, relief='ridge')
    test3_frame = LabelFrame(root, text='3', font=14, bd=2, relief='ridge')
    test4_frame = LabelFrame(root, text='4', font=14, bd=2, relief='ridge')
    test5_frame = LabelFrame(root, text='5', font=14, bd=2, relief='ridge')
    test6_frame = LabelFrame(root, text='6', font=14, bd=2, relief='ridge')
    test7_frame = LabelFrame(root, text='7', font=14, bd=2, relief='ridge')
    test8_frame = LabelFrame(root, text='8', font=14, bd=2, relief='ridge')
    test9_frame = LabelFrame(root, text='9', font=14, bd=2, relief='ridge')
    test10_frame = LabelFrame(root, text='10', font=14, bd=2, relief='ridge')
    test11_frame = LabelFrame(root, text='11', font=14, bd=2, relief='ridge')
    test12_frame = LabelFrame(root, text='12', font=14, bd=2, relief='ridge')
    test13_frame = LabelFrame(root, text='13', font=14, bd=2, relief='ridge')
    test14_frame = LabelFrame(root, text='14', font=14, bd=2, relief='ridge')
    test15_frame = LabelFrame(root, text='15', font=14, bd=2, relief='ridge')
    
    test1_frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
    test2_frame.grid(row=1, column=0, sticky='nsew', padx=2, pady=2)
    test3_frame.grid(row=2, column=0, sticky='nsew', padx=2, pady=2)
    test4_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
    test5_frame.grid(row=4, column=0, sticky='nsew', padx=2, pady=2)
    
    test6_frame.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)
    test7_frame.grid(row=1, column=1, sticky='nsew', padx=2, pady=2)
    test8_frame.grid(row=2, column=1, sticky='nsew', padx=2, pady=2)
    test9_frame.grid(row=3, column=1, sticky='nsew', padx=2, pady=2)
    test10_frame.grid(row=4, column=1, sticky='nsew', padx=2, pady=2)
    
    test11_frame.grid(row=0, column=2, sticky='nsew', padx=2, pady=2)
    test12_frame.grid(row=1, column=2, sticky='nsew', padx=2, pady=2)
    test13_frame.grid(row=2, column=2, sticky='nsew', padx=2, pady=2)
    test14_frame.grid(row=3, column=2, sticky='nsew', padx=2, pady=2)
    test15_frame.grid(row=4, column=2, sticky='nsew', padx=2, pady=2)
    
    
    # ## Page layout
    # header_frame = LabelFrame(root, bd=1, relief='flat')
    # treeview1_frame = LabelFrame(root, text='100% Oil', font=14, bd=2, relief='ridge')
    # treeview2_frame = LabelFrame(root, text='x% Oil', font=14, bd=2, relief='ridge')
    # plot1_frame = LabelFrame(root, text='Coolant Temp vs Time', font=14, bd=2, relief='ridge')
    # plot2_frame = LabelFrame(root, text='Coolant Temp vs RPM', font=14, bd=2, relief='ridge')
    # plot3_frame = LabelFrame(root, text='RPM % Change', font=14, bd=2, relief='ridge')
    # button_frame = LabelFrame(root, text='Options', font=14, bd=2, relief='ridge')
    # info_frame = LabelFrame(root, text='Info', font=14, bd=2, relief='ridge')

    # header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
    # treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
    # treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
    # plot1_frame.grid(row=1, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    # plot2_frame.grid(row=2, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    # plot3_frame.grid(row=3, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
    # button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
    # info_frame.grid(row=3, column=1, columnspan=1, sticky='nsew', padx=2, pady=2)
    
    # # Widgets
    # page_title = Label(header_frame, text='UConn FSAE DAQ Multitool')
    # page_title.place(relx=.5, rely=.5, anchor=CENTER)
    # page_title.config(font=('arial', 14))
    
    # ## Treeview 1 widget
    # tree1_data = ttk.Treeview(treeview1_frame)
    # tree1_data.place(relheight=1, relwidth=1)
    # treescrolly = Scrollbar(tree1_data, orient='vertical', command=tree1_data.yview)
    # treescrollx = Scrollbar(tree1_data, orient='horizontal', command=tree1_data.xview)
    # tree1_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    # treescrollx.pack(side='bottom', fill='x')
    # treescrolly.pack(side='right', fill='y')    
    
    # ## Treeview 2 widget
    # tree2_data = ttk.Treeview(treeview2_frame)
    # tree2_data.place(relheight=1, relwidth=1)
    # treescrolly = Scrollbar(tree2_data, orient='vertical', command=tree2_data.yview)
    # treescrollx = Scrollbar(tree2_data, orient='horizontal', command=tree2_data.xview)
    # tree2_data.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    # treescrollx.pack(side='bottom', fill='x')
    # treescrolly.pack(side='right', fill='y')    
    
    # ## Main Buttons
    # button1 = Button(button_frame, text='Oil File 1', command=lambda: False)
    # button1.place(y=30, relx=.25, width=80, anchor=CENTER)

    # button2 = Button(button_frame, text='Oil File 2', command=lambda: False)
    # button2.place(y=70, relx=.25, width=80, anchor=CENTER)

    # button3 = Button(button_frame, text='Clear Data', command=lambda: False)
    # button3.place(y=30, relx=.75, width=80, anchor=CENTER)

    # button4 = Button(button_frame, text='Process Data', command=lambda: False)
    # button4.place(y=70, relx=.75, width=80, anchor=CENTER)
    
    # ## Statistics
    # filepath_label1 = Label(info_frame, text='File 1: ', wraplength=450, justify=LEFT)
    # filepath_label1.place(y=10, x=10)

    # filepath_label2 = Label(info_frame, text='File 2: ', wraplength=450, justify=LEFT)
    # filepath_label2.place(y=55, x=10)

    # stat1_label = Label(info_frame, text=' ', wraplength=350, justify=LEFT)
    # stat1_label.place(y=75, x=10)

    # stat2_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    # stat2_label.place(y=95, x=10)

    # stat3_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    # stat3_label.place(y=115, x=10)
    
    # stat4_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
    # stat4_label.place(y=135, x=10)
    
    # # Graph Buttons
    # graph_button1 = Button(plot1_frame, text='Graph 1', command=lambda: create_window(graph_button1['text']))
    # graph_button1.place(rely=.5, relx=.5, width=80, anchor=CENTER)

    # graph_button2 = Button(plot2_frame, text='Graph 2', command=lambda: create_window(graph_button2['text']))
    # graph_button2.place(rely=.5, relx=.5, width=80, anchor=CENTER)

    # graph_button3 = Button(plot3_frame, text='Graph 3', command=lambda: create_window(graph_button3['text']))
    # graph_button3.place(rely=.5, relx=.5, width=80, anchor=CENTER)
    
    main_btn()

    return None


limp_mode_page()
root.mainloop()