# Refer to this post to understand the foundation of the code.
# This will explain the purpose of the App class and the child Page classes.
# https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# https://github.com/TomSchimansky/CustomTkinter/wiki/Packaging
# Look into https://nuitka.net/ for packaging

import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import pandas as pd

import constants as c
import functions as f
import sector_analysis as sa
import downforce_analysis as da
import oil_analysis as oa
# from functions import format_data

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('Multifunction Staistics Tool')
        self.geometry('700x600')

        # GUI variables
        self.col_options_list = ['Columns'] # this will be the columns from input csv
        self.var_col_choice = tk.StringVar()
        self.var_col_choice.set(self.col_options_list[0])

        # Used in session_analysis_page and sector_analysis_page
        self.normalize_stationary_bool = tk.BooleanVar(value=False)
        self.rmv_stationary_bool = tk.BooleanVar(value=False)

        # Used in limp_mode_page
        self.spinbox_max_temp_diff_from_avg = tk.IntVar(value=c.MAX_TEMP_DIFF_FROM_AVG)

        # Dataframe dictionary
        # Stores temporary data files when a user input is required.
        # Is cleared whenever the user changes pages (back to main menu)
        self.datafiles = {}

        self._frame = None
        self.switch_frame(MainMenuPage)

    def switch_frame(self, frame_class: object):
        if self._frame is not None:
            self._frame.destroy()
        
        self.datafiles.clear()
        
        # place holder to export processed data
        self.datafiles['analysis'] = {'path': '', 'dataframe': ''}

        new_frame = frame_class(self)
        
        # Set grid of parent frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._frame = new_frame
        self._frame.grid(sticky='nsew')
        

    def select_aim_file(self, data_name: str):
        try: 
            filepath = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                                ('All Files', '*.*')))
            if filepath == '' or filepath is None:
                return None

            df_input = pd.read_fwf(filepath, header=None, encoding='ISO-8859-1').reset_index(drop=True)
            df_formatted_data = f.format_data(df_input)

            # this dictionary format allows us to add future information about a data file
            data_info = {'path': filepath, 'dataframe': df_formatted_data}

            self.datafiles[data_name] = data_info
            print(app.datafiles)

            return self.datafiles[data_name]['dataframe']

        except:
            messagebox.showerror('Warning', 'File is not compatible. \nEnsure the file is in the AiM format.')

    def select_file(self, data_name: str):
        filepath = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                            ('All Files', '*.*')))
        if filepath == '' or filepath is None:
            return None

        df_input = pd.read_csv(filepath, encoding='ISO-8859-1').reset_index(drop=True)

        # this dictionary format allows us to add future information about a data file
        data_info = {'path': filepath, 'dataframe': df_input}

        self.datafiles[data_name] = data_info
        print(self.datafiles)

        return self.datafiles[data_name]['dataframe']

    def ask_for_data_file(self, parent: object, tree: object, data_name: str, label: str, aim_data_bool: bool):
        if aim_data_bool:    
            try:
                TreeViewWidget.display_csv(tree, app.select_aim_file(data_name))
            except:
                return None
        else:
            try:
                TreeViewWidget.display_csv(tree, app.select_file(data_name))
            except:
                return None

        filepath = app.datafiles[data_name]['path']
        df = app.datafiles[data_name]['dataframe']

        leading_label = label['text'].split(':')[0] + ':'
        label['text'] = f'{leading_label} {filepath}'

        parent.optionmenu_var_col['menu'].delete(0, 'end')


        # Insert list of new options (tk._setit hooks them up to var)
        if aim_data_bool:
            new_cols = df.columns
            for col in new_cols:
                parent.optionmenu_var_col['menu'].add_command(label=col, command=tk._setit(app.var_col_choice, col))

            app.var_col_choice.set(new_cols[-1])


    def create_output_path(self, analysis_name: str, file_extension: str):
        date = dt.datetime.now()
        timestamp = date.strftime('%m-%d-%Y_%H-%M-%S')
        new_path = c.output_folder + analysis_name + '_' + timestamp  + '.' + file_extension

        return new_path


class MainMenuPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = tk.LabelFrame(self, text='Page: Main Menu', relief='ridge')
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_rowconfigure(2, weight=1)
        # container.grid_rowconfigure(3, weight=2)

        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=3)
        container.grid_columnconfigure(2, weight=3)

        # Page Widgets (temporary)
        for i in range(3):
            label = tk.Label(container, text=f'Test {i}')
            label.grid(row=i, column=i, sticky='nsew')
        
        btn1 = tk.Button(container, text='Session Analysis', command=lambda: parent.switch_frame(SessionAnalysisPage))
        btn1.grid(row=0, column=0, sticky='nsew')

        btn2 = tk.Button(container, text='Sector Analysis', command=lambda: parent.switch_frame(SectorAnalysisPage))
        btn2.grid(row=1, column=0, sticky='nsew')
        
        btn3 = tk.Button(container, text='Coastdown Analysis', command=lambda: parent.switch_frame(CoastdownPage))
        btn3.grid(row=2, column=0, sticky='nsew')
        
        btn4 = tk.Button(container, text='Oil Analysis', command=lambda: parent.switch_frame(OilAnalysisPage))
        btn4.grid(row=2, column=1, sticky='nsew')

class SessionAnalysisPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.output_path = ''
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = tk.LabelFrame(self, text='Page: Session Analysis', relief='ridge')
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=4)
        container.grid_rowconfigure(2, weight=4)
        container.grid_rowconfigure(3, weight=4)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)
        # container.grid_columnconfigure(2, weight=2)

        # Page Widgets
        header_frame = tk.LabelFrame(container, bd=1, relief='flat')
        treeview1_frame = tk.LabelFrame(container, text='Session Data', font=14, bd=2, relief='ridge')
        treeview2_frame = tk.LabelFrame(container, text='Session Analysis', font=14, bd=2, relief='ridge')
        button_frame = tk.LabelFrame(container, text='Options', font=14, bd=2, relief='ridge')
        info_frame = tk.LabelFrame(container, text='Info', font=14, bd=2, relief='ridge')

        header_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
        treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
        treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
        button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=1, sticky='nsew', padx=2, pady=2)

        page_title = tk.Label(header_frame, text='UConn FSAE DAQ Multitool')
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)
        page_title.config(font=('arial', 14))

        # Header buttons
        main_btn = MainMenuButton(self, header_frame)
        export_btn = ExportButton(self, header_frame)

        # Treeviews
        tree1 = TreeViewWidget(treeview1_frame)
        tree2 = TreeViewWidget(treeview2_frame)

        ## Main Buttons
        # button1 = tk.Button(button_frame, text='Data File', command=lambda: TreeViewWidget.display_csv(tree1, app.select_aim_file(self, 'aimdata1')))
        button1 = tk.Button(button_frame, text='Data File', command=lambda: app.ask_for_data_file(self, tree1, 'aimdata1', self.inputpath1_label, aim_data_bool=True))
        button1.place(y=30, relx=.25, width=80, anchor=tk.CENTER)

        button2 = tk.Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1, tree2], [self.inputpath1_label, self.outputpath_label]))
        button2.place(y=70, relx=.25, width=80, anchor=tk.CENTER)

        # button3 = Button(button_frame, text='Process Data', command=lambda: session_analysis(df_data, var_col_choice))
        button3 = tk.Button(button_frame, text='Process Data', command=lambda: self.process_session_analysis(tree2, 'aimdata1'))
        button3.place(y=30, relx=.75, width=80, anchor=tk.CENTER)

        # Options
        # These are self variables since we need to modify their attributes later on
        self.optionmenu_var_col = tk.OptionMenu(button_frame, app.var_col_choice, *app.col_options_list, command=lambda x: print(f'OptionMenu: {x}'))
        self.optionmenu_var_col.place(y=70, relx=.75, anchor=tk.CENTER)

        self.checkbox_normalize = tk.Checkbutton(button_frame, text='Normalize stationary Values (description)', 
                                variable=app.normalize_stationary_bool, onvalue=1, offvalue=0, justify=tk.LEFT)
        self.checkbox_normalize.place(y=122, relx=.5, anchor=tk.CENTER)

        self.checkbox_rmv_stationary = tk.Checkbutton(button_frame, text='Remove stationary values (description)    ', 
                                variable=app.rmv_stationary_bool, onvalue=1, offvalue=0, justify=tk.LEFT)
        self.checkbox_rmv_stationary.place(y=142, relx=.5, anchor=tk.CENTER)

        ## Statistics
        self.inputpath1_label = tk.Label(
            info_frame, 
            text='File 1: ',
            wraplength=450,
            justify=tk.LEFT)
        self.inputpath1_label.place(y=10, x=10)

        self.outputpath_label = tk.Label(
            info_frame, 
            text='Output: ',
            wraplength=450,
            justify=tk.LEFT)
        self.outputpath_label.place(y=45, x=10)

        info1_label = tk.Label(
            info_frame, 
            text='Mandatory columns:\nTime, Distance',
            wraplength=350,
            justify=tk.LEFT)
        info1_label.place(y=95, x=10)

    def process_session_analysis(self, tree, data_name):
        df_processed = f.basic_stats(
                        app.datafiles[data_name]['dataframe'], 
                        app.var_col_choice.get(), 
                        app.normalize_stationary_bool.get(), 
                        app.rmv_stationary_bool.get()
                        )
        clear_treeview([tree], [])
        TreeViewWidget.display_csv(tree, df_processed)

        filepath = app.create_output_path('session_analysis', 'csv')
        app.datafiles['analysis'] = {'path': filepath, 'dataframe': df_processed}

class SectorAnalysisPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = tk.LabelFrame(self, text='Page: Sector Analysis', relief='ridge')
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=4)
        container.grid_rowconfigure(2, weight=4)
        container.grid_rowconfigure(3, weight=4)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)
        container.grid_columnconfigure(2, weight=2)

        ## Page Widgets
        header_frame = tk.LabelFrame(container, bd=1, relief='flat')
        treeview1_frame = tk.LabelFrame(container, text='Session Data', font=14, bd=2, relief='ridge')
        treeview2_frame = tk.LabelFrame(container, text='Sectors', font=14, bd=2, relief='ridge')
        treeview3_frame = tk.LabelFrame(container, text='Analysis', font=14, bd=2, relief='ridge')
        button_frame = tk.LabelFrame(container, text='Options', font=14, bd=2, relief='ridge')
        info_frame = tk.LabelFrame(container, text='Info', font=14, bd=2, relief='ridge')

        header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
        treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
        treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
        treeview3_frame.grid(row=1, rowspan=2, column=2, sticky='nsew', padx=2, pady=2)
        button_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=2, columnspan=2, sticky='nsew', padx=2, pady=2)
        
        # Widgets
        page_title = tk.Label(header_frame, text='UConn FSAE DAQ Multitool')
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)
        page_title.config(font=('arial', 14))
        
        main_btn = MainMenuButton(self, header_frame)
        export_btn = ExportButton(self, header_frame)

        # Treeviews
        tree1 = TreeViewWidget(treeview1_frame)
        tree2 = TreeViewWidget(treeview2_frame)
        tree3 = TreeViewWidget(treeview3_frame)
        
        ## Main Buttons
        button1 = tk.Button(button_frame, text='Data File', command=lambda: app.ask_for_data_file(self, tree1, 'aimdata1', self.inputpath1_label, aim_data_bool=True))
        button1.place(y=30, relx=.25, width=80, anchor=tk.CENTER)

        # button2 = tk.Button(button_frame, text='Sectors File', command=lambda: TreeViewWidget.display_csv(tree2, app.select_file(self, 'sectors')))
        button2 = tk.Button(button_frame, text='Sectors File', command=lambda: app.ask_for_data_file(self, tree2, 'sectors', self.inputpath2_label, aim_data_bool=False))
        button2.place(y=70, relx=.25, width=80, anchor=tk.CENTER)

        button3 = tk.Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1, tree2, tree3], [self.inputpath1_label, self.inputpath2_label, self.outputpath_label]))
        button3.place(y=30, relx=.75, width=80, anchor=tk.CENTER)
        # **
        button4 = tk.Button(button_frame, text='Process Data', command=lambda: self.process_sector_analysis(tree3))
        button4.place(y=70, relx=.75, width=80, anchor=tk.CENTER)
        
        ## Options
        self.optionmenu_var_col = tk.OptionMenu(button_frame, app.var_col_choice, *app.col_options_list, command=lambda x: print(f'OptionMenu: {x}'))
        self.optionmenu_var_col.place(y=110, relx=.25, anchor=tk.CENTER)

        self.checkbox_normalize = tk.Checkbutton(button_frame, text='Normalize stationary\nvalues (description)', 
                                variable=app.normalize_stationary_bool, onvalue=1, offvalue=0, justify=tk.LEFT)
        self.checkbox_normalize.place(y=110, relx=.75, anchor=tk.CENTER)

        self.checkbox_rmv_stationary = tk.Checkbutton(button_frame, text='Remove stationary\nvalues (description)    ', 
                                variable=app.rmv_stationary_bool, onvalue=1, offvalue=0, justify=tk.LEFT)
        self.checkbox_rmv_stationary.place(y=150, relx=.75, anchor=tk.CENTER)

        ## Statistics
        self.inputpath1_label = tk.Label(
            info_frame,
            text='File 1: ',
            wraplength=450,
            justify=tk.LEFT)
        self.inputpath1_label.place(y=10, x=10)

        self.inputpath2_label = tk.Label(info_frame, text='File 2: ', wraplength=450, justify=tk.LEFT)
        self.inputpath2_label.place(y=45, x=10)

        self.outputpath_label = tk.Label(
            info_frame, 
            text='Output: ',
            wraplength=450,
            justify=tk.LEFT)
        self.outputpath_label.place(y=65, x=10)

        stat1_label = tk.Label(info_frame, text=' ', wraplength=350, justify=tk.LEFT)
        stat1_label.place(y=95, x=10)

        stat2_label = tk.Label(info_frame, text='Mandatory columns: Time, Distance', wraplength=350, justify=tk.LEFT)
        stat2_label.place(y=1055, x=10)

        # stat3_label = tk.Label(info_frame, text='Time, Distance ', wraplength=350, justify=tk.LEFT)
        # stat3_label.place(y=115, x=10)
        
        # stat4_label = Label(info_frame, text='Text ', wraplength=350, justify=LEFT)
        # stat4_label.place(y=135, x=10)

    def process_sector_analysis(self, treeview):
        # helper function to get dataframe from session_analysis and display to GUI
        print('Sector Analysis')
        print(app.datafiles)
        df_analysis = sa.init_sector_analysis(
                            app.datafiles['aimdata1']['dataframe'], 
                            app.datafiles['sectors']['dataframe'], 
                            app.var_col_choice.get(), 
                            app.normalize_stationary_bool.get(),
                            app.rmv_stationary_bool.get()
                            )
        
        filepath = app.create_output_path('session_analysis', 'csv')
        app.datafiles['analysis'] = {'path': filepath, 'dataframe': df_analysis}
        
        df_analysis['Stats'] = c.SECTOR_STATS_LABELS

        first_column = df_analysis.pop('Stats')
        df_analysis.insert(0, 'Stats', first_column)

        TreeViewWidget.display_csv(treeview, df_analysis)


class CoastdownPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = tk.LabelFrame(self, text='Page: Coastdown Analysis', relief='ridge')
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=2)
        container.grid_rowconfigure(2, weight=2)
        container.grid_rowconfigure(3, weight=2)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)
        container.grid_columnconfigure(2, weight=2)

        ## Page layout
        header_frame = tk.LabelFrame(container, bd=1, relief='flat')
        treeview1_frame = tk.LabelFrame(container, text='Coastdown Data', font=14, bd=2, relief='ridge')
        plot1_frame = tk.LabelFrame(container, text='Downforce vs Speed', font=14, bd=2, relief='ridge')
        button_frame = tk.LabelFrame(container, text='Options', font=14, bd=2, relief='ridge')
        info_frame = tk.LabelFrame(container, text='Info', font=14, bd=2, relief='ridge')

        header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
        treeview1_frame.grid(row=1, rowspan=2, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
        plot1_frame.grid(row=1, rowspan=2, column=2, sticky='nsew', padx=2, pady=2)
        button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=1, columnspan=2, sticky='nsew', padx=2, pady=2)
        
        # Widgets
        page_title = tk.Label(header_frame, text='UConn FSAE DAQ Multitool')
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)
        page_title.config(font=('arial', 14))
        
        main_btn = MainMenuButton(header_frame)

        ## Treeview 1 widget   
        tree1 = TreeViewWidget(treeview1_frame)

        ## Main Buttons
        button1 = tk.Button(button_frame, text='Data File', command=lambda: select_datafile1(tree1_data, filepath_label1))
        button1.place(y=30, relx=.25, width=80, anchor=tk.CENTER)

        button2 = tk.Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1_data], [filepath_label1]))
        button2.place(y=70, relx=.25, width=80, anchor=tk.CENTER)

        button3 = tk.Button(button_frame, text='Process Data', command=lambda: popup_graph(
            init_downforce_analysis(df_data1),
            create_window('Downforce vs Speed')))
        button3.place(y=70, relx=.75, width=80, anchor=tk.CENTER)
        
        ## Statistics
        filepath_label1 = tk.Label(info_frame, text='File 1: ', wraplength=450, justify=tk.LEFT)
        filepath_label1.place(y=10, x=10)

        stat1_label = tk.Label(info_frame, text=' ', wraplength=350, justify=tk.LEFT)
        stat1_label.place(y=75, x=10)

        stat2_label = tk.Label(info_frame, text='Mandatory columns:', wraplength=350, justify=tk.LEFT)
        stat2_label.place(y=95, x=10)

        stat3_label = tk.Label(info_frame, text='Time, Distance, YawRate, Front_Left_Forc, Front_Right_Forc, Rear_Right_Force, Rear_Left_Force, S8_tps1, F_Brake_Press, R_Brake_Pres, GPS_Speed',
            wraplength=350, justify=tk.LEFT)
        stat3_label.place(y=115, x=10)

class OilAnalysisPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = tk.LabelFrame(self, text='Page: Oil Analysis', relief='ridge')
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=3)
        container.grid_rowconfigure(2, weight=3)
        container.grid_rowconfigure(3, weight=3)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)
        container.grid_columnconfigure(2, weight=1)

        ## Page layout
        header_frame = tk.LabelFrame(container, bd=1, relief='flat')
        treeview1_frame = tk.LabelFrame(container, text='100% Oil', font=14, bd=2, relief='ridge')
        treeview2_frame = tk.LabelFrame(container, text='x% Oil', font=14, bd=2, relief='ridge')
        plot1_frame = tk.LabelFrame(container, text='Coolant Temp vs Time', font=14, bd=2, relief='ridge')
        plot2_frame = tk.LabelFrame(container, text='Coolant Temp vs RPM', font=14, bd=2, relief='ridge')
        plot3_frame = tk.LabelFrame(container, text='RPM % Change', font=14, bd=2, relief='ridge')
        button_frame = tk.LabelFrame(container, text='Options', font=14, bd=2, relief='ridge')
        info_frame = tk.LabelFrame(container, text='Info', font=14, bd=2, relief='ridge')

        header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=2)
        treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
        treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
        plot1_frame.grid(row=1, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
        plot2_frame.grid(row=2, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
        plot3_frame.grid(row=3, rowspan=1, column=2, sticky='nsew', padx=2, pady=2)
        button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=1, columnspan=1, sticky='nsew', padx=2, pady=2)
        
        # Widgets
        page_title = tk.Label(header_frame, text='UConn FSAE DAQ Multitool')
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)
        page_title.config(font=('arial', 14))
        
        main_btm = MainMenuButton(header_frame)

        ## Treeviews
        tree1 = TreeViewWidget(treeview1_frame)
        tree2 = TreeViewWidget(treeview2_frame)
        
        ## Main Buttons
        button1 = tk.Button(button_frame, text='Oil File 1', command=lambda: select_datafile1(tree1, filepath_label1))
        button1.place(y=30, relx=.25, width=80, anchor=tk.CENTER)

        button2 = tk.Button(button_frame, text='Oil File 2', command=lambda: select_datafile2(tree2, filepath_label2))
        button2.place(y=70, relx=.25, width=80, anchor=tk.CENTER)

        button3 = tk.Button(button_frame, text='Clear Data', command=lambda: clear_treeview([tree1, tree2], [filepath_label1, filepath_label2]))
        button3.place(y=30, relx=.75, width=80, anchor=tk.CENTER)

        button4 = tk.Button(button_frame, text='Process Data', command=lambda: init_oil_analysis([df_data1, df_data2], int(app.spinbox_max_temp_diff_from_avg.get()))) # ** displays all graphs at once.
        button4.place(y=70, relx=.75, width=80, anchor=tk.CENTER)

        spinbox1 = tk.Spinbox(button_frame, from_=0, to=99, textvariable=app.spinbox_max_temp_diff_from_avg)
        spinbox1.place(y=140, relx=.25, width=80, anchor=tk.CENTER)
        spinbox1_label = tk.Label(button_frame, text='Max temperature difference from\naverage (used to remove outliers)')
        spinbox1_label.place(relx=.25, y=110, anchor=tk.CENTER)

        ## Statistics
        filepath_label1 = tk.Label(info_frame, text='File 1: ', wraplength=450, justify=tk.LEFT)
        filepath_label1.place(y=10, x=10)

        filepath_label2 = tk.Label(info_frame, text='File 2: ', wraplength=450, justify=tk.LEFT)
        filepath_label2.place(y=55, x=10)

        stat1_label = tk.Label(info_frame, text=' ', wraplength=350, justify=tk.LEFT)
        stat1_label.place(y=75, x=10)

        stat2_label = tk.Label(info_frame, text='Mandatory columns:', wraplength=350, justify=tk.LEFT)
        stat2_label.place(y=95, x=10)

        stat3_label = tk.Label(info_frame, text='Time, Distance, S8_RPM, S*eot, S8_ect1, S8_eop', wraplength=350, justify=tk.LEFT)
        stat3_label.place(y=115, x=10)


class MainMenuButton():
    def __init__(self, parent, frame):
        main_menu_btn = tk.Button(frame, text='Main Menu', command=lambda: app.switch_frame(MainMenuPage))
        main_menu_btn.place(x=0, y=0)

        # Reset variables
        # GUI variables
        app.col_options_list = ['Columns'] # this will be the columns from input csv
        app.var_col_choice = tk.StringVar()
        app.var_col_choice.set(app.col_options_list[0])

        # Used in session_analysis_page and sector_analysis_page
        app.normalize_stationary_bool = tk.BooleanVar(value=False)
        app.rmv_stationary_bool = tk.BooleanVar(value=False)

        # Used in limp_mode_page
        app.spinbox_max_temp_diff_from_avg = tk.IntVar(value=c.MAX_TEMP_DIFF_FROM_AVG)


class ExportButton():
    def __init__(self, parent, frame):
        self.parent = parent

        export_button = tk.Button(frame, text='Export Data', command=lambda: self.export_df_to_csv())
        export_button.pack(anchor='ne', side='top')

    def export_df_to_csv(self):
        df = app.datafiles['analysis']['dataframe']
        path = app.datafiles['analysis']['path']
        
        if isinstance(df, pd.DataFrame):
            print(path)
            df.to_csv(path, index=False)
        
        self.update_output_label(path)

    def update_output_label(self, path):
        self.parent.output_label['text'] = f'Output: {path}'

class TreeViewWidget(ttk.Treeview):
    def __init__(self, parent):
        ttk.Treeview.__init__(self, parent)

        self.place(relheight=1, relwidth=1)
        treescrolly = ttk.Scrollbar(self, orient='vertical', command=self.yview)
        treescrollx = ttk.Scrollbar(self, orient='horizontal', command=self.xview)
        self.config(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        
        treescrollx.pack(side='bottom', fill='x')
        treescrolly.pack(side='right', fill='y')


    def display_csv(self, df):
        ## Code to display dataframe in tree-view
        self['columns'] = list(df.columns) # ex) data['attribute']
        self['show'] = 'headings'
        for column in self['columns']:
            self.heading(column, text=column)
        
        df_rows = df.to_numpy().tolist()
        for row in df_rows: # for each row in df, insert into tree view
            self.insert('', 'end', values=row)

        list_headers = df.columns.values.tolist()
        for column in list_headers:
            self.column(column, width=10, stretch=tk.YES)

    # def clear_treeview(self, trees, lables: list):
    #     # print(type(trees))
    #     for treeview in trees:
    #         treeview.delete(*treeview.get_children())
    #     treeview['columns'] = [None]
        
    #     if lables is None:
    #         return None
    #     else:
    #         for label in lables:
    #             label['text'] = label['text'].split(':')[0] + ':'

class StatisticsFrame():
    def __init__(self, parent):
        pass

def clear_treeview(trees, lables: list):
    # print(type(trees))
    for treeview in trees:
        treeview.delete(*treeview.get_children())
        treeview['columns'] = [None]
    
    if lables is None:
        return None
    else:
        for label in lables:
            label['text'] = label['text'].split(':')[0] + ':'

# def output_sector_analysis(treeview, df):
#     # helper function to get dataframe from session_analysis and display to GUI


#     df['Stats'] = c.SECTOR_STATS_LABELS

#     first_column = df.pop('Stats')
#     df.insert(0, 'Stats', first_column)

#     TreeViewWidget.display_csv(treeview, df)

#     return df


if __name__ == '__main__':
    app = App()
    app.mainloop()