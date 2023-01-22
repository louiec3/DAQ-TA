###############################################################
# DAQ TA
# 
# DAQ TA is a tool to automate the process of converting AiM 
# files from Race Studio to generate statistics and graphs for 
# certain tests.
# 
# Copyright (c) 2023 Louis Cundari III. All rights reserved.
# Louis Cundari III
# louiscundari3@outlook.com
###############################################################

# Refer to this post to understand the foundation of the GUI code (object oriented programming with tkinter).
# This will explain the purpose of the App class and the child Page classes.
# https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter

import customtkinter as ctk
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

BUTTONS_WIDTH = 100

class App(ctk.CTk):
    def __init__(self):
        ctk.CTk.__init__(self)

        ctk.set_appearance_mode('System')
        self.iconbitmap('logo.ico')

        self.title('Multifunction Staistics Tool')
        self.geometry('700x600')

        # GUI variables
        self.col_options_list = ['Columns'] # this will be the columns from input csv
        self.var_col_choice = ctk.StringVar()
        self.var_col_choice.set(self.col_options_list[0])

        # Used in session_analysis_page and sector_analysis_page
        self.normalize_stationary_bool = ctk.BooleanVar(value=False)
        self.rmv_stationary_bool = ctk.BooleanVar(value=False)

        # Used in limp_mode_page
        self.spinbox_max_temp_diff_from_avg = ctk.IntVar(value=c.MAX_TEMP_DIFF_FROM_AVG)

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
        filepath = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                            ('All Files', '*.*')))
        if filepath == '' or filepath is None:
            return None

        df_input = pd.read_fwf(filepath, header=None, encoding='ISO-8859-1').reset_index(drop=True)
        
        try: 
            df_formatted_data = f.format_data(df_input)

            # this dictionary format allows us to add future information about a data file
            data_info = {'path': filepath, 'dataframe': df_formatted_data}

            self.datafiles[data_name] = data_info
            # print(app.datafiles)

            return self.datafiles[data_name]['dataframe']

        except Exception as e:
            print(e)
            messagebox.showerror('Warning', f'Error: {e}\n\nFile is not compatible. \nEnsure the file is in the AiM format.')

    def select_file(self, data_name: str):
        filepath = filedialog.askopenfilename(title='Select a File', filetype=(('CSV Files', '*.csv *.xlsx *.xls *.xlsb *.xlsm'),
                                                                            ('All Files', '*.*')))

        if filepath == '' or filepath is None:
            return None

        df_input = pd.read_csv(filepath, encoding='ISO-8859-1').reset_index(drop=True)

        # this dictionary format allows us to add future information about a data file
        data_info = {'path': filepath, 'dataframe': df_input}

        self.datafiles[data_name] = data_info
        # print(self.datafiles)

        return self.datafiles[data_name]['dataframe']

    def ask_for_data_file(self, parent: object, tree: object, data_name: str, label: str, aim_data_bool: bool, update_col_options_bool: bool):
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

        leading_label = label.cget('text').split(':')[0] + ':'
        label.configure(text=f'{leading_label} {filepath}')

        # Insert list of new options (tk._setit hooks them up to var)
        if update_col_options_bool:
            # parent.optionmenu_var_col['menu'].delete(0, 'end')
            new_cols = df.columns
            # for col in new_cols:
            #     parent.optionmenu_var_col['menu'].add_command(label=col, command=tk._setit(app.var_col_choice, col))

            app.var_col_choice.set(new_cols[-1])
            parent.optionmenu_var_col.configure(values=new_cols, variable=app.var_col_choice)

    def create_output_path(self, analysis_name: str, file_extension: str):
        date = dt.datetime.now()
        timestamp = date.strftime('%m-%d-%Y_%H-%M-%S')
        new_path = c.output_folder + analysis_name + '_' + timestamp  + '.' + file_extension

        return new_path

    def create_window(self, window_name):
        graph_window = ctk.CTkToplevel(self)
        graph_window.wm_title(window_name)
        
        return graph_window

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

class MainMenuPage(ctk.CTkFrame):
    def __init__(self, parent):
        # tk.Frame.__init__(self, parent)
        ctk.CTkFrame.__init__(self, parent)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_rowconfigure(2, weight=1)

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(2, weight=1)


        # buttons_container = ctk.CTkFrame(container)
        # buttons_container.grid(row=1, column=1)
        # Page Widgets (temporary)
        # for i in range(3):
        #     label = ctk.CTkLabel(container, text=f'Test {i}')
        #     label.grid(row=i, column=i, sticky='nsew')
        
        title_label = ctk.CTkLabel(
            container, 
            text=f'DAQ TA', 
            font=ctk.CTkFont(size=38)
            )
        title_label.grid(row=0, column=1, sticky='nsew')
        
        btn1 = ctk.CTkButton(
            container, 
            text='Session Analysis', 
            command=lambda: parent.switch_frame(SessionAnalysisPage)
            )
        btn1.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

        btn2 = ctk.CTkButton(
            container, 
            text='Sector Analysis', 
            command=lambda: parent.switch_frame(SectorAnalysisPage)
            )
        btn2.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)
        
        btn3 = ctk.CTkButton(
            container, 
            text='Coastdown Analysis', 
            command=lambda: parent.switch_frame(CoastdownPage)
            )
        btn3.grid(row=2, column=1, sticky='nsew', padx=10, pady=10)
        
        btn4 = ctk.CTkButton(
            container, 
            text='Oil Analysis', 
            command=lambda: parent.switch_frame(OilAnalysisPage)
            )
        btn4.grid(row=2, column=2, sticky='nsew', padx=10, pady=10)
        
        # btn5 = ctk.CTkButton(container, text='Oil Analysis', command=lambda: parent.switch_frame(OilAnalysisPage))
        appearance_mode_optionemenu = ctk.CTkOptionMenu(
            container, 
            values=['System', 'Dark', 'Light'],
            command=lambda x: app.change_appearance_mode(x)
            )
        appearance_mode_optionemenu.place(x=0, y=0)

class SessionAnalysisPage(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # container = tk.LabelFrame(self, text='Page: Session Analysis', relief='ridge')
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=4)
        container.grid_rowconfigure(2, weight=4)
        container.grid_rowconfigure(3, weight=4)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)

        # Page containers
        header_frame = ctk.CTkFrame(container)
        treeview1_frame = ctk.CTkFrame(container)
        treeview2_frame = ctk.CTkFrame(container)
        button_frame = ctk.CTkFrame(container)
        info_frame = ctk.CTkFrame(container)

        header_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
        treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=5, pady=5)
        treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=5, pady=5)
        button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=1, sticky='nsew', padx=2, pady=2)

        # Configure header_frame
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        # Configure button_frame grid
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        button_frame.grid_rowconfigure(3, weight=1)
        button_frame.grid_rowconfigure(4, weight=1)
        button_frame.grid_rowconfigure(5, weight=1)
        button_frame.grid_rowconfigure(6, weight=1)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Header widgets
        page_title = ctk.CTkLabel(
            header_frame, 
            text='DAQ TA: Session Analysis', 
            font=ctk.CTkFont(size=18)
            )
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)

        main_btn = MainMenuButton(self, header_frame)
        export_btn = ExportButton(self, header_frame)

        # Treeviews
        tree1 = TreeViewWidget(treeview1_frame)
        tree2 = TreeViewWidget(treeview2_frame)

        ## Main Buttons
        button1 = ctk.CTkButton(
            button_frame, 
            text='Data File',
            width=BUTTONS_WIDTH,
            command=lambda: app.ask_for_data_file(
                self, 
                tree1, 
                'aimdata1', 
                self.inputpath1_label, 
                aim_data_bool=True, 
                update_col_options_bool=True
                )
            )
        # button1.place(y=30, relx=.25, width=90, anchor=tk.CENTER)
        button1.grid(row=1, column=0)

        # These are self variables since we need to modify their attributes later on
        self.optionmenu_var_col = ctk.CTkOptionMenu(
            master=button_frame,
            width=BUTTONS_WIDTH,
            values=app.col_options_list,
            command=lambda x: print(f'Column selected: {x}')
            )
        # self.optionmenu_var_col.place(y=70, relx=.75, anchor=tk.CENTER)
        self.optionmenu_var_col.grid(row=2, column=0)

        self.checkbox_normalize = ctk.CTkCheckBox(
            button_frame, 
            text='Normalize stationary\nvalues',
            variable=app.normalize_stationary_bool, 
            onvalue=1, 
            offvalue=0, 
            checkbox_width=20,
            checkbox_height=20
            )
        # self.checkbox_normalize.place(y=120, relx=.5, anchor=tk.CENTER)
        self.checkbox_normalize.grid(row=3, column=0)

        self.checkbox_rmv_stationary = ctk.CTkCheckBox(
            button_frame, 
            text='Remove stationary\nvalues', 
            variable=app.rmv_stationary_bool, 
            onvalue=1, 
            offvalue=0, 
            checkbox_width=20,
            checkbox_height=20
            )
        # self.checkbox_rmv_stationary.place(y=145, relx=.5, anchor=tk.CENTER)
        self.checkbox_rmv_stationary.grid(row=4, column=0)

        button2 = ctk.CTkButton(
            button_frame, 
            text='Clear Data',
            width=BUTTONS_WIDTH, 
            command=lambda: clear_treeview(
                [tree1, tree2], 
                [self.inputpath1_label,
                 self.outputpath_label]
                )
            )
        # button2.place(y=70, relx=.25, width=90, anchor=tk.CENTER)
        button2.grid(row=1, column=1)

        button3 = ctk.CTkButton(
            button_frame,
            text='Process',
            width=BUTTONS_WIDTH,
            command=lambda: self.process_session_analysis(
                tree2,
                'aimdata1'
                )
            )
        # button3.place(y=30, relx=.75, width=90, anchor=tk.CENTER)
        button3.grid(row=2, column=1)


        ## Info Frame
        self.inputpath1_label = ctk.CTkLabel(
            info_frame, 
            text='File 1: ',
            wraplength=450,
            justify=tk.LEFT
            )
        self.inputpath1_label.place(y=10, x=10)

        self.outputpath_label = ctk.CTkLabel(
            info_frame, 
            text='Output: ',
            wraplength=450,
            justify=tk.LEFT
            )
        self.outputpath_label.place(y=45, x=10)

        info1_label = ctk.CTkLabel(
            info_frame, 
            text='Mandatory columns:\nTime, Distance',
            wraplength=350,
            justify=tk.LEFT)
        info1_label.place(y=95, x=10)

    def process_session_analysis(self, tree, data_name):
        try:
            df_processed = f.basic_stats(
                            app.datafiles[data_name]['dataframe'], 
                            app.var_col_choice.get(), 
                            app.normalize_stationary_bool.get(), 
                            app.rmv_stationary_bool.get()
                            )
            clear_treeview([tree], [])

            filepath = app.create_output_path('session_analysis', 'csv')
            app.datafiles['analysis'] = {'path': filepath, 'dataframe': df_processed}
            
            TreeViewWidget.display_csv(tree, df_processed)
        except KeyError as e:
            if str(e) == 'aimdata1':
                print('No data selected.')
        except:
            raise

class SectorAnalysisPage(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=4)
        container.grid_rowconfigure(2, weight=4)
        container.grid_rowconfigure(3, weight=4)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)
        container.grid_columnconfigure(2, weight=2)

        ## Page containers
        header_frame = ctk.CTkFrame(container)
        treeview1_frame = ctk.CTkFrame(container)
        treeview2_frame = ctk.CTkFrame(container)
        treeview3_frame = ctk.CTkFrame(container)
        button_frame = ctk.CTkFrame(container)
        info_frame = ctk.CTkFrame(container)

        header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew')
        treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
        treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
        treeview3_frame.grid(row=1, rowspan=2, column=2, sticky='nsew', padx=2, pady=2)
        button_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=2, columnspan=2, sticky='nsew', padx=2, pady=2)
        
        # Configure header_frame
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        # Configure button_frame grid
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        button_frame.grid_rowconfigure(3, weight=1)
        button_frame.grid_rowconfigure(4, weight=1)
        button_frame.grid_rowconfigure(5, weight=1)
        button_frame.grid_rowconfigure(6, weight=1)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Header widgets
        page_title = ctk.CTkLabel(
            header_frame, 
            text='DAQ TA: Sector Analysis', 
            font=ctk.CTkFont(size=18)
            )
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)
        
        main_btn = MainMenuButton(self, header_frame)
        export_btn = ExportButton(self, header_frame)

        # Treeviews
        tree1 = TreeViewWidget(treeview1_frame)
        tree2 = TreeViewWidget(treeview2_frame)
        tree3 = TreeViewWidget(treeview3_frame)
        
        ## Main Buttons
        button1 = ctk.CTkButton(
            button_frame, 
            text='Data File', 
            width=BUTTONS_WIDTH,
            command=lambda: app.ask_for_data_file(
                self, 
                tree1, 
                'aimdata1', 
                self.inputpath1_label, 
                aim_data_bool=True, 
                update_col_options_bool=True
                )
            )
        # button1.place(y=30, relx=.25, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button1.grid(row=1, column=0)

        button2 = ctk.CTkButton(
            button_frame, 
            text='Sectors File', 
            width=BUTTONS_WIDTH,
            command=lambda: app.ask_for_data_file(
                self, 
                tree2, 
                'sectors', 
                self.inputpath2_label, 
                aim_data_bool=False, 
                update_col_options_bool=False
                )
            )
        # button2.place(y=70, relx=.25, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button2.grid(row=2, column=0)

        ## Options (compare this section to SessionAnalysisPage)        
        self.optionmenu_var_col = ctk.CTkOptionMenu(
            master=button_frame, 
            width=BUTTONS_WIDTH,
            values=app.col_options_list, 
            command=lambda x: print(f'Column selected: {x}')
            )
        # self.optionmenu_var_col.place(y=110, relx=.25, anchor=tk.CENTER)
        self.optionmenu_var_col.grid(row=3, column=0)

        self.checkbox_normalize = ctk.CTkCheckBox(
            button_frame, 
            text='Normalize stationary\nvalues',
            variable=app.normalize_stationary_bool, 
            onvalue=1, 
            offvalue=0, 
            checkbox_width=20,
            checkbox_height=20
            )
        # self.checkbox_normalize.place(y=110, relx=.5, anchor=tk.CENTER)
        self.checkbox_normalize.grid(row=4, column=0)

        self.checkbox_rmv_stationary = ctk.CTkCheckBox(
            button_frame, 
            text='Remove stationary\nvalues',
            variable=app.rmv_stationary_bool, 
            onvalue=1, 
            offvalue=0, 
            checkbox_width=20,
            checkbox_height=20
            )
        # self.checkbox_rmv_stationary.place(y=150, relx=.5, anchor=tk.CENTER)
        self.checkbox_rmv_stationary.grid(row=5, column=0)
        
        button3 = ctk.CTkButton(
            button_frame, 
            text='Clear Data',
            width=BUTTONS_WIDTH,
            command=lambda: clear_treeview(
                [tree1, tree2, tree3], 
                [self.inputpath1_label, self.inputpath2_label, self.outputpath_label]
                )
            )
        # button3.place(y=30, relx=.75, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button3.grid(row=1, column=1)

        button4 = ctk.CTkButton(
            button_frame, 
            text='Process', 
            width=BUTTONS_WIDTH,
            command=lambda: self.process_sector_analysis(tree3) ## ** check to see if a name needs to be given (compare to process_session_analysis)
            )
        # button4.place(y=70, relx=.75, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button4.grid(row=2, column=1)

        ## Info Frame
        self.inputpath1_label = ctk.CTkLabel(
            info_frame,
            text='File 1: ',
            wraplength=450,
            justify=tk.LEFT)
        self.inputpath1_label.place(y=10, x=10)

        self.inputpath2_label = ctk.CTkLabel(
            info_frame, 
            text='File 2: ',
            wraplength=450, 
            justify=tk.LEFT
            )
        self.inputpath2_label.place(y=45, x=10)

        self.outputpath_label = ctk.CTkLabel(
            info_frame, 
            text='Output: ',
            wraplength=450,
            justify=tk.LEFT
            )
        self.outputpath_label.place(y=80, x=10)

        stat1_label = ctk.CTkLabel(
            info_frame, 
            text='Mandatory columns:\nTime, Distance\n\nOptional Track Map Columns:\nGPS Latitude, GPS Longitude', 
            wraplength=350, 
            justify=tk.LEFT
            )
        stat1_label.place(y=155, x=10)

    def process_sector_analysis(self, tree):
        # helper function to get dataframe from session_analysis and display to GUI
        try:
            df_analysis = sa.init_sector_analysis(
                                app.datafiles['aimdata1']['dataframe'], 
                                app.datafiles['sectors']['dataframe'], 
                                app.var_col_choice.get(), 
                                app.normalize_stationary_bool.get(),
                                app.rmv_stationary_bool.get()
                                )
            clear_treeview([tree], [])
            filepath = app.create_output_path('session_analysis', 'csv')
            app.datafiles['analysis'] = {'path': filepath, 'dataframe': df_analysis}
            
            df_analysis['Stats'] = c.SECTOR_STATS_LABELS

            first_column = df_analysis.pop('Stats')
            df_analysis.insert(0, 'Stats', first_column)

            TreeViewWidget.display_csv(tree, df_analysis)
        except KeyError:
            print('No data selected.')

class CoastdownPage(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=4)
        container.grid_rowconfigure(2, weight=4)
        container.grid_rowconfigure(3, weight=4)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)

        # Page containers
        header_frame = ctk.CTkFrame(container)
        treeview1_frame = ctk.CTkFrame(container)
        button_frame = ctk.CTkFrame(container)
        info_frame = ctk.CTkFrame(container)

        header_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
        treeview1_frame.grid(row=1, column=0, columnspan=2, rowspan=2, sticky='nsew', padx=5, pady=5)
        button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=1, sticky='nsew', padx=2, pady=2)

        # Configure header_frame
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        # Configure button_frame
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        button_frame.grid_rowconfigure(3, weight=1)
        button_frame.grid_rowconfigure(4, weight=1)
        button_frame.grid_rowconfigure(5, weight=1)
        button_frame.grid_rowconfigure(6, weight=1)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Header widgets
        page_title = ctk.CTkLabel(header_frame, text='DAQ TA: Coastdown Analysis', font=ctk.CTkFont(size=18))
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)
        
        main_btn = MainMenuButton(self, header_frame)
        # export_btn = ExportButton(self, header_frame)


        ## Treeview widget   
        tree1 = TreeViewWidget(treeview1_frame)

        ## Main Buttons
        # button1 = tk.Button(button_frame, text='Data File', command=lambda: select_datafile1(tree1_data, filepath_label1))
        button1 = ctk.CTkButton(
            button_frame, 
            text='Data File',
            width=BUTTONS_WIDTH, 
            command=lambda: app.ask_for_data_file(
                self, 
                tree1, 
                'aimdata1', 
                self.inputpath1_label, 
                aim_data_bool=True, 
                update_col_options_bool=False
                )
            )
        # button1.place(y=30, relx=.25, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button1.grid(row=1, column=0)

        button2 = ctk.CTkButton(
            button_frame, 
            text='Clear Data',
            width=BUTTONS_WIDTH, 
            command=lambda: clear_treeview(
                [tree1], 
                [self.inputpath1_label]
                )
            )
        # button2.place(y=70, relx=.25, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button2.grid(row=1, column=1)

        # button3 = tk.Button(button_frame, text='Process', command=lambda: self.popup_graph(
        #     da.init_downforce_analysis(df_data1),
        #     create_window('Downforce vs Speed')))
        button3 = ctk.CTkButton(
            button_frame, 
            text='Process',
            width=BUTTONS_WIDTH, 
            command=lambda: self.process_coastdown_analysis(app.datafiles['aimdata1']['dataframe']))
        # button3.place(y=70, relx=.75, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button3.grid(row=2, column=1)

        ## Statistics
        self.inputpath1_label = ctk.CTkLabel(
            info_frame, 
            text='File 1: ',
            wraplength=450, 
            justify=tk.LEFT
            )
        self.inputpath1_label.place(y=10, x=10)

        stat1_label = ctk.CTkLabel(
            info_frame, 
            text=' ', 
            wraplength=350, 
            justify=tk.LEFT
            )
        stat1_label.place(y=75, x=10)

        stat2_label = ctk.CTkLabel(
            info_frame, 
            text='Mandatory columns:', 
            wraplength=350, 
            justify=tk.LEFT
            )
        stat2_label.place(y=95, x=10)

        stat3_label = ctk.CTkLabel(
            info_frame, 
            text='Time, Distance, YawRate, Front_Left_Forc, Front_Right_Forc, Rear_Right_Force, Rear_Left_Force, S8_tps1, F_Brake_Press, R_Brake_Pres, GPS_Speed',
            wraplength=350, 
            justify=tk.LEFT
            )
        stat3_label.place(y=115, x=10)

    def process_coastdown_analysis(self, df):
        try:
            fig = da.init_downforce_analysis(df)
            print(fig)
            fig.show()
        except KeyError:
            print('No data selected.')
        except:
            raise

class OilAnalysisPage(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky='nsew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=3)
        container.grid_rowconfigure(2, weight=3)
        container.grid_rowconfigure(3, weight=3)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=2)
        # container.grid_columnconfigure(2, weight=1)

        ## Page layout
        header_frame = ctk.CTkFrame(container)
        treeview1_frame = ctk.CTkFrame(container)
        treeview2_frame = ctk.CTkFrame(container)
        button_frame = ctk.CTkFrame(container)
        info_frame = ctk.CTkFrame(container)

        header_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
        treeview1_frame.grid(row=1, rowspan=2, column=0, sticky='nsew', padx=2, pady=2)
        treeview2_frame.grid(row=1, rowspan=2, column=1, sticky='nsew', padx=2, pady=2)
        button_frame.grid(row=3, column=0, sticky='nsew', padx=2, pady=2)
        info_frame.grid(row=3, column=1, columnspan=1, sticky='nsew', padx=2, pady=2)
        
        # Configure header_frame
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        # Configure button_frame grid
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        button_frame.grid_rowconfigure(3, weight=1)
        button_frame.grid_rowconfigure(4, weight=1)
        button_frame.grid_rowconfigure(5, weight=1)
        button_frame.grid_rowconfigure(6, weight=1)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Widgets
        page_title = ctk.CTkLabel(
            header_frame, 
            text='DAQ TA: Oil Analysis', 
            font=ctk.CTkFont(size=18)
            )
        page_title.place(relx=.5, rely=.5, anchor=tk.CENTER)
        
        main_btm = MainMenuButton(self, header_frame)

        ## Treeviews
        tree1 = TreeViewWidget(treeview1_frame)
        tree2 = TreeViewWidget(treeview2_frame)
        
        ## Main Buttons
        button1 = ctk.CTkButton(
            button_frame, 
            text='Oil File 1',
            width=BUTTONS_WIDTH, 
            command=lambda: app.ask_for_data_file(
                self, 
                tree1, 
                'aimdata1', 
                self.inputpath1_label, 
                aim_data_bool=True, 
                update_col_options_bool=False
                )
            )
        # button1.place(y=30, relx=.25, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button1.grid(row=1, column=0)

        button2 = ctk.CTkButton(
            button_frame, 
            text='Oil File 2',
            width=BUTTONS_WIDTH, 
            command=lambda: app.ask_for_data_file(
                self, 
                tree2, 
                'aimdata2', 
                self.inputpath2_label, 
                aim_data_bool=True, 
                update_col_options_bool=False
                )
            )
        # button2.place(y=70, relx=.25, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button2.grid(row=2, column=0)

        spinbox1 = tk.Spinbox(
            button_frame, 
            from_=0, 
            to=99, 
            width=18,
            textvariable=app.spinbox_max_temp_diff_from_avg
            )
        # spinbox1.place(y=130, relx=.25, anchor=tk.CENTER)
        spinbox1.grid(row=3, column=0)

        spinbox1_label = ctk.CTkLabel(
            button_frame, 
            text='Max temperature difference from\naverage (used to remove outliers)'
            )
        # spinbox1_label.place(relx=.25, y=180, anchor=tk.CENTER)
        spinbox1_label.grid(row=4, column=0)

        button3 = ctk.CTkButton(
            button_frame, 
            text='Clear Data',
            width=BUTTONS_WIDTH, 
            command=lambda: clear_treeview(
                [tree1, tree2], 
                [self.inputpath1_label, self.inputpath2_label]
                )
            )
        # button3.place(y=30, relx=.75, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button3.grid(row=1, column=1)


        # button4 = tk.Button(button_frame, text='Process', command=lambda: init_oil_analysis([df_data1, df_data2], int(app.spinbox_max_temp_diff_from_avg.get()))) # ** displays all graphs at once.
        button4 = ctk.CTkButton(
            button_frame, 
            text='Process',
            width=BUTTONS_WIDTH, 
            command=lambda: self.process_oil_analysis(
                app.datafiles['aimdata1']['dataframe'], 
                app.datafiles['aimdata2']['dataframe']
                )
            ) # ** displays all graphs at once.
        # button4.place(y=70, relx=.75, width=BUTTONS_WIDTH, anchor=tk.CENTER)
        button4.grid(row=2, column=1)

        ## Statistics
        self.inputpath1_label = ctk.CTkLabel(
            info_frame, 
            text='File 1: ', 
            wraplength=450, 
            justify=tk.LEFT
            )
        self.inputpath1_label.place(y=10, x=10)

        self.inputpath2_label = ctk.CTkLabel(
            info_frame, 
            text='File 2: ', 
            wraplength=450, 
            justify=tk.LEFT
            )
        self.inputpath2_label.place(y=55, x=10)

        stat1_label = ctk.CTkLabel(
            info_frame, 
            text='Mandatory columns:', 
            wraplength=350, 
            justify=tk.LEFT
            )
        stat1_label.place(y=95, x=10)

        stat2_label = ctk.CTkLabel(
            info_frame, 
            text='Time, Distance, S8_RPM, S8_eot, S8_ect1, S8_eop', 
            wraplength=350,
            justify=tk.LEFT
            )
        stat2_label.place(y=115, x=10)

    def process_oil_analysis(self, df1, df2):
        try:
            print(f'Max temp diff: {app.spinbox_max_temp_diff_from_avg.get()}')
            oa.init_oil_analysis([df1, df2], int(app.spinbox_max_temp_diff_from_avg.get()))
        except ValueError as e:
            if str(e) == 'No objects to concatenate':
                print('Max temperature difference is too low. Raise the value and try again.')
        except:
            raise

class MainMenuButton():
    def __init__(self, parent, frame):
        main_menu_btn = ctk.CTkButton(
            frame, 
            text='Main Menu',
            width=BUTTONS_WIDTH,
            command=lambda: app.switch_frame(MainMenuPage)
            )
        # main_menu_btn.place(x=0, y=0)
        main_menu_btn.grid(row=0, column=0, sticky='nw')
        # cannot pack two items on same row
        # **solution can be to create a 2 column grid for header_frame

        # Reset App() variables
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

        export_btn = ctk.CTkButton(
            frame,
            text='Export Data', 
            width=BUTTONS_WIDTH,
            command=lambda: self.export_df_to_csv()
            )
        # export_btn.pack(anchor='ne', side='top')
        export_btn.grid(row=0, column=1, sticky='ne')        

    def export_df_to_csv(self):
        df = app.datafiles['analysis']['dataframe']
        path = app.datafiles['analysis']['path']
        
        if isinstance(df, pd.DataFrame):
            print(path)
            df.to_csv(path, index=False)
            messagebox.showinfo(title='Information', message=f'File saved successfully:\n{path}')
        
        self.update_outputpath_label(path)

    def update_outputpath_label(self, path):
        self.parent.outputpath_label.configure(text=f'Output: {path}')

class TreeViewWidget(ttk.Treeview):
    def __init__(self, parent):
        ttk.Treeview.__init__(self, parent)

        ## ** test other styles
        style = ttk.Style(app)
        style.theme_use('winnative')
        style.configure('Treeview', background='#2b2b2b', 
                        fieldbackground='#2b2b2b', foreground='white')
        
        # https://stackoverflow.com/questions/47642635/automatic-minimum-width-for-column-0-in-tkinter-treeview
        style.configure('Treeview.Heading', font=(None, 10))

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
            # label['text'] = label['text'].split(':')[0] + ':' # for tkinter
            leading_label = label.cget('text').split(':')[0] + ':'
            label.configure(text=f'{leading_label}')


if __name__ == '__main__':
    app = App()
    app.mainloop()