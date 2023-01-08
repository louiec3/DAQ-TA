# Refer to this post to understand the foundation of the code.
# This will explain the purpose of the App class and the child Page classes.
# https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter

import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import constants as c

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('Multifunction Staistics Tool')
        self.geometry('450x400')

        self._frame = None
        self.switch_frame(MainMenuPage)

        # GUI variables
        self.col_options_list = ['Columns'] # this will be the columns from input csv
        self.var_col_choice = tk.StringVar()
        self.var_col_choice.set(self.col_options_list[0])

        # Used in session_analysis_page and sector_analysis_page
        self.normalize_stationary_bool = tk.BooleanVar(value=False)
        self.rmv_stationary_bool = tk.BooleanVar(value=False)

        # Used in limp_mode_page
        self.spinbox_max_temp_diff_from_avg = tk.IntVar(value=c.MAX_TEMP_DIFF_FROM_AVG)


    def switch_frame(self, frame_class):
        # Destroys current frame and replaces it with a new one.
        if self._frame is not None:
            self._frame.destroy()
        
        new_frame = frame_class(self)
        
        # Set grid of parent frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._frame = new_frame
        self._frame.grid(sticky='nsew')

class MainMenuPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = tk.LabelFrame(self, text='Page Container Start', relief='ridge')
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=2)
        container.grid_rowconfigure(2, weight=2)
        # container.grid_rowconfigure(3, weight=2)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)
        container.grid_columnconfigure(2, weight=2)

        # Page Widgets (temporary)
        for i in range(3):
            label = tk.Label(container, text=f'Test {i}')
            # label.pack(side='top', fill='x', pady=10)
            label.grid(row=i, column=i, sticky='nsew')
        
        btn1 = tk.Button(container, text='Page 1', command=lambda: parent.switch_frame(SessionAnalysisPage))
        btn1.grid(row=0, column=0, sticky='nsew')

        btn2 = tk.Button(container, text='Page 2', command=lambda: parent.switch_frame(SectorAnalysisPage))
        btn2.grid(row=1, column=0, sticky='nsew')
        
        btn3 = tk.Button(container, text='Page 3', command=lambda: parent.switch_frame(CoastDownPage))
        btn3.grid(row=1, column=0, sticky='nsew')
        
        btn4 = tk.Button(container, text='Page 4', command=lambda: parent.switch_frame(OilAnalysisPage))
        btn4.grid(row=1, column=0, sticky='nsew')

class SessionAnalysisPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = tk.LabelFrame(self, text='Page Container Session', relief='ridge')
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=2)
        container.grid_rowconfigure(2, weight=2)
        container.grid_rowconfigure(3, weight=2)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)
        # container.grid_columnconfigure(2, weight=2)

        # Page Widgets

        header_frame = tk.LabelFrame(container, bd=1, relief='flat')
        treeview1_frame = tk.LabelFrame(container, text='Session Data', font=14, bd=2, relief='ridge')
        treeview2_frame = tk.LabelFrame(container, text='Session Analysis', font=14, bd=2, relief='ridge')
        button_frame = tk.LabelFrame(container, text='Options', font=14, bd=2, relief='ridge')
        info_frame = tk.LabelFrame(container, text='Info', font=14, bd=2, relief='ridge')

        header_frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        treeview1_frame.grid(row=1, rowspan=2, column=0, columnspan=1, sticky='nsew', padx=2, pady=2)
        treeview2_frame.grid(row=1, rowspan=2, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
        button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=1, sticky='nsew', padx=2, pady=2)

        page_title = tk.Label(header_frame, text='UConn FSAE DAQ Multitool')
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)
        page_title.config(font=('arial', 14))

        main_btn = MainMenuButton(header_frame)
        tree1 = TreeViewWidget(treeview1_frame)
        tree2 = TreeViewWidget(treeview2_frame)

        ## Main Buttons
        button1 = tk.Button(button_frame, text='Data File', command=lambda: select_datafile1(tree1_data, filepath_label1))
        button1.place(y=30, relx=.25, width=80, anchor=tk.CENTER)

        button2 = tk.Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data, tree2_data], [filepath_label1]))
        button2.place(y=70, relx=.25, width=80, anchor=tk.CENTER)

        # button3 = Button(button_frame, text='Process Data', command=lambda: session_analysis(df_data, var_col_choice))
        button3 = tk.Button(button_frame, text='Process Data', command=lambda: output_session_analysis(basic_stats(df_data1, var_col_choice.get(), normalize_stationary_bool.get(), rmv_stationary_bool.get()), tree2_data))
        button3.place(y=30, relx=.75, width=80, anchor=tk.CENTER)

        # **export_button = tk.Button(tree2_data, text='Export Data', command=lambda: export_df_to_csv(df_sector_analysis, c.sector_analysis_path))
        # export_button.pack(anchor='se', side='bottom')

        ## Options
        # col_options_list; this list variable could update when a file is inputed and filled in with available columns
        optionmenu_var_col = tk.OptionMenu(button_frame, App.var_col_choice, *App.col_options_list, command=lambda x: print(f'OptionMenu: {x}'))
        optionmenu_var_col.place(y=70, relx=.75, anchor=tk.CENTER)

        checkbox_normalize = tk.Checkbutton(button_frame, text='Normalize stationary Values (description)', 
                                variable=App.normalize_stationary_bool, onvalue=1, offvalue=0, justify=tk.LEFT)
        checkbox_normalize.place(y=122, relx=.5, anchor=tk.CENTER)

        checkbox_rmv_stationary = tk.Checkbutton(button_frame, text='Remove stationary values (description)    ', 
                                variable=App.rmv_stationary_bool, onvalue=1, offvalue=0, justify=tk.LEFT)
        checkbox_rmv_stationary.place(y=142, relx=.5, anchor=tk.CENTER)

        ## Statistics
        filepath_label1 = tk.Label(info_frame, text='File 1: ', wraplength=450, justify=tk.LEFT)
        filepath_label1.place(y=10, x=10)

        stat1_label = tk.Label(info_frame, text=' ', wraplength=350, justify=tk.LEFT)
        stat1_label.place(y=75, x=10)

        stat2_label = tk.Label(info_frame, text='''
                                        Mandatory columns:\n
                                        Time, Distance
                                        '''
                                        , wraplength=350, justify=tk.LEFT)
        stat2_label.place(y=95, x=10)

        stat3_label = tk.Label(info_frame, text='Time, Distance', wraplength=350, justify=tk.LEFT)
        stat3_label.place(y=115, x=10)

class SectorAnalysisPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text='This is Page 2').pack(side='top', fill='x', pady=10)
        tk.Button(self, text='Return to start page',
                  command=lambda: parent.switch_frame(MainMenuPage)).pack()

class CoastDownPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text='This is Page 2').pack(side='top', fill='x', pady=10)
        tk.Button(self, text='Return to start page',
                  command=lambda: parent.switch_frame(MainMenuPage)).pack()

class OilAnalysisPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text='This is Page 2').pack(side='top', fill='x', pady=10)
        tk.Button(self, text='Return to start page',
                  command=lambda: parent.switch_frame(MainMenuPage)).pack()

class MainMenuButton():
    def __init__(self, parent):
        main_menu_btn = tk.Button(parent, text='Main Menu', command=MainMenuPage)
        main_menu_btn.place(x=0, y=0)
        

class TreeViewWidget(ttk.Treeview):
    def __init__(self, parent):
        ttk.Treeview.__init__(self, parent)

        self.place(relheight=1, relwidth=1)
        treescrolly = ttk.Scrollbar(self, orient='vertical', command=self.yview)
        treescrollx = ttk.Scrollbar(self, orient='horizontal', command=self.xview)
        self.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        
        treescrollx.pack(side='bottom', fill='x')
        treescrolly.pack(side='right', fill='y')  



if __name__ == '__main__':
    app = App()
    app.mainloop()