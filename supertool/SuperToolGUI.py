# SuperToolGUI.py, Charlie Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import json
import os
import pathvalidate
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import tkinter.filedialog  as fd


import supertool.consts as consts
from supertool.SuperToolFrames import *
import supertool.SuperToolProject.Project as stproject
import supertool.ScriptListener as ScriptListener

from supertool.ProjectView import ProjectView
from supertool.TestView import TestView, kill_pslf
from supertool.ParamView import ParamView

class SuperToolGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        ### setup root window
        self.title("Super Tool")
        self.iconphoto(True, tk.PhotoImage(file="./icons/supertoolplay.png"))
        # remove the tear off option from the top menu bar
        self.option_add('*tearOff', tk.FALSE)
        
        # Allows the main frame to be resizeable with the window
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # project is the backend project object that the ui interacts with
        # focused_test is the test to show in the test_view panel
        self.project = stproject.Project()
        self.focused_test = None
        
        # setup backend listener script and its boolean signal flag
        self.running = True
        self.listener = ScriptListener.ScriptListener(self)
        self.listener.start()
        
        # run the helper methods to set up widgets and full window keybinds
        self.widgets()
        self.keybinds()
        
        # these 2 lines set the minimum size of the window to its initial size
        # @TODO may need to mess with this later but it's fine for now, is update necessary?
        self.update()
        self.minsize(500,250)
        # print(self.winfo_width(), self.winfo_height())
        
        def on_quit():
            # set running to false, indicating that the listener thread should stop
            self.running = False
            print("===== Waiting for ScriptListener to finish =====")
            self.listener.join()
            print("===== ScriptListener has finished  =====")
            
            # close the window
            self.destroy()
            
            # save use pslf gui value
            print("===== Saving Modified Configuration Data =====")
            try:
                consts.config_data['HIDE_PSLF_GUI'] = self.hide_pslf_gui.get()
                json.dump(consts.config_data, open('config.json', 'w'), indent=4)
                print("===== Modified Configuration Data Saved =====")
            except FileNotFoundError:
                print("ERROR: Failed to open config.json. Runtime settings not saved.")
            
            # close the pslf window while we're on the way out
            print("===== Closing PSLF =====")
            kill_pslf()
            print("===== PSLF Closed =====")

        self.protocol('WM_DELETE_WINDOW', on_quit)
        

    # helper method to create and add all of the high level widgets to the 
    # main window. also handles making each row and column resize-able
    def widgets(self):
        ### Frame creation
        # main frame setup, row and column configure for initial size and resizeability
        self.grid_rowconfigure(0, minsize=150, weight=1)
        self.grid_columnconfigure(0, minsize=50, weight=1)
        self.grid_columnconfigure(1, minsize=50, weight=1)
        self.grid_columnconfigure(2, minsize=50, weight=1)

        # create the sub-frames
        self.proj_frame = ProjectView(self)
        self.test_frame = TestView(self)
        self.param_frame = ParamView(self)
        self.statusbar_frame = StatusBar(self)
        
        # place the sub-frames into the main window
        self.proj_frame.grid(row=0,column=0, columnspan=1, rowspan=1, sticky="nesw")
        self.test_frame.grid(row=0,column=1, columnspan=1, rowspan=1, sticky="nesw")
        self.param_frame.grid(row=0,column=2, columnspan=1, rowspan=1, sticky="nesw")
        self.statusbar_frame.grid(row=1, column=0, columnspan=3, sticky="nesw")

        # top bar menu setup
        self.menu()

    # helper method to set up main window keybinds
    # @TODO check if these are still active in the plot popup
    def keybinds(self):
        self.bind("<F5>", self.test_frame.run_simulation)
        self.bind("<Control-F5>", lambda e:
            self.test_frame.run_simulation(save_on_run=False))
        self.bind("<Control-o>", self.open_project)
        self.bind("<Control-s>", self.save_project)
        self.bind("<Control-n>", self.new_project)
        self.bind("<Control-S>", self.save_as_project)
        
    # helper method to set up the main file menu at the top of the
    # window. The run menu is also used as a context menu for 
    # test view.
    def menu(self):
        # create and set menu as the applications titlebar menu
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        
        # sub-menu creation
        file_menu = tk.Menu(self.menubar)
        about_menu = tk.Menu(self.menubar)
        self.run_menu = tk.Menu(self.menubar)
        self.graph_menu = tk.Menu(self.menubar)
        

        # add options to the file menu
        # accelerators don't actually do anything, they need to be set
        # in the keybinds method
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="ctrl+n") #@TODO make the accelerators do something
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator="ctrl+o")
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator="ctrl+s")
        file_menu.add_command(label="Save Project As", command=self.save_as_project, accelerator="ctrl+shift+s")
        file_menu.add_separator()
        file_menu.add_command(label="New Unit", command=print)
        file_menu.add_command(label="New Test")
        # file_menu.add_separator()
        # file_menu.add_command(label="Open Workspace", command=open_workspace)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy)

        # add options to the run menu
        self.run_menu.add_command(label="Run", command=self.test_frame.run_simulation, accelerator="F5")
        self.run_menu.add_command(label="Run Without Saving",
            command=lambda: self.test_frame.run_simulation(save_on_run=False),
            accelerator="ctrl+F5")
        self.run_menu.add_separator()
        # tk boolean variable for if pslf should be run with or without its gui
        self.hide_pslf_gui = tk.BooleanVar(value=consts.HIDE_PSLF_GUI)
        self.last_hide_pslf_gui_val = None
        self.run_menu.add_radiobutton(label="Run PSLF with GUI", variable=self.hide_pslf_gui, value=False)
        self.run_menu.add_radiobutton(label="Run PSLF without GUI", variable=self.hide_pslf_gui, value=True)

        # add options to the graph menu
        self.graph_menu.add_command(label="Graph", command=self.param_frame.graph)
        self.graph_menu.add_command(label="Graph Without Saving",
            command=lambda: self.param_frame.graph(save_on_graph=False))

        # add options to the about menu
        about_menu.add_command(label="About")
        about_menu.add_command(label="Version")
        
        # add the submenus to the menu bar
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menubar.add_cascade(label="Run", menu=self.run_menu)
        self.menubar.add_cascade(label="Graph", menu=self.graph_menu)
        self.menubar.add_cascade(label="About", menu=about_menu)
    
    # wrapper for statusbar text setting
    # needs some work
    def set_status(self, string):
        self.statusbar_frame.set_text(string)
    
    # method called by ctrl+n and the file menu
    # shows a prompt asking for a new file name and
    # creates a new project
    # @TODO make the prompt a custom window and institute some error checking
    def _new_project(self, e=None):
        # confirmation and entry popup
        new_project_name = simpledialog.askstring(title="New Project", 
            prompt="Enter a name for the new project.\nAll unsaved progress will be lost.")
        if new_project_name:
            # delete current project class
            del self.project
            self.project = stproject.Project(new_project_name)
            # re-render project pane
            self.proj_frame.render()
            # clear test view
            self.focused_test = None
            self.test_frame.show_focused_test()
            self.param_frame.render()
    
    def new_project(self, e=None):
        new_proj_window = BaseOkPopup(self, "New Project")
        
        name_var = tk.StringVar(self)
        save_var = tk.StringVar(self)
        dir_var = tk.StringVar(self)
        
        def save_select(e=None):
            # save file as dialog
            filename = fd.asksaveasfilename(defaultextension="*.*", filetypes=[("Super Tool Project Files", "*.pec")])
            if filename:
                save_var.set(filename)
        
        def dir_select(e=None):
            dirname = fd.askdirectory(mustexist=True)
            if dirname:
                dir_var.set(dirname)
        
        def ok_command(e=None):
            proj_name = name_var.get()
            save_file = save_var.get()
            work_dir = dir_var.get()
            message_list = []
            
            if proj_name:
                # check for weird characters?
                pass
            else:
                message_list.append("Please enter a name for the project.")
        
            if save_file:
                if not os.path.exists(os.path.dirname(save_file)):
                    message_list.append("Invalid save file path entered")
                elif os.path.isdir(save_file):
                    message_list.append("The entered save file should be a file, not a directory")
                if not pathvalidate.is_valid_filename(os.path.basename(save_file)):
                    message_list.append("The entered save file contains illegal characters for a file name")
            if work_dir:
                if work_dir[-1] in '/\\':
                    work_dir = work_dir[:-1]
                
                if os.path.exists(work_dir):
                    # if it's not a directory, complain
                    if not os.path.isdir(work_dir):
                        message_list.append("The entered working directory is not a directory.")
                else:
                    message_list.append("The entered working directory does not exist.")
            else:
                message_list.append("Please enter a working directory for the project.")
        
            if message_list:
                # update the screen with errors
                new_proj_window.show_errors(message_list)
            else:
                new_proj_window.hide_errors()
            
                # close the new project window
                new_proj_window.destroy()
                
                # delete current project class
                del self.project
                self.project = stproject.Project(proj_name) # @TODO set work directory and save file name
                if save_file:
                    self.project.file_name = save_file
                    self.save_project()
                self.project.working_dir = work_dir
                self.set_project
                # re-render project pane
                self.proj_frame.render()
                self.proj_frame.update_proj_header()
                # clear test view
                self.focused_test = None
                self.test_frame.show_focused_test()
                self.param_frame.render()
        
        def cancel_command(e=None):
            new_proj_window.destroy()
        
        name_frame = ttk.Frame(new_proj_window.frame)
        name_frame.grid(row=0, sticky='nesw')
        name_frame.columnconfigure(0, weight=1)
        name_frame.columnconfigure(1, weight=1)
        name_label = ttk.Label(name_frame,
                text="Enter a name for the new project.")
        name_label.grid(row=0, column=0, sticky='w')
        name_entry = ttk.Entry(name_frame, textvariable=name_var, width=25)
        name_entry.grid(row=0, column=1, sticky='ew')
        # give the entry keyboard focus
        name_entry.focus_set()
        
        save_frame = ttk.Frame(new_proj_window.frame)
        save_frame.grid(row=1, sticky='nesw')
        save_label = ttk.Label(save_frame,
                text="Enter a save file name for the project.\nLeave blank to choose a save location later.") #, wraplength=225)
        save_label.grid(row=0, column=0, sticky='w', columnspan=2)
        save_entry = ttk.Entry(save_frame, textvariable=save_var, width=45)
        save_entry.grid(row=1, column=0)
        save_select_button = ttk.Button(save_frame, text="Choose File",
                                        command=save_select)
        save_select_button.grid(row=1, column=1, sticky='ew')
        save_select_button.bind("<Return>", save_select)
        
        dir_frame = ttk.Frame(new_proj_window.frame)
        dir_frame.grid(row=2, sticky='nesw')
        dir_label = ttk.Label(dir_frame,
                text="Choose a working directory. The project save file does not need\n" \
                   + "to be inside the working directory, but every file necessary\n" \
                   + "for PSLF (sav, dyd, csv) will need to be there.")
        dir_label.grid(row=0, column=0, sticky='w', columnspan=2)
        dir_entry = ttk.Entry(dir_frame, textvariable=dir_var, width=45)
        dir_entry.grid(row=1, column=0)
        dir_select_button = ttk.Button(dir_frame, text="Choose Folder",
                                       command=dir_select)
        dir_select_button.grid(row=1, column=1, sticky='ew')
        dir_select_button.bind("<Return>", dir_select)
        
        new_proj_window.wrapup(ok_command=ok_command, cancel_command=cancel_command)
        
        
    # method called by ctrl+o and the file menu
    # shows a prompt allowing the user to select a pec file to open
    # then opens the file
    def open_project(self, e=None):
        filename = fd.askopenfilename(filetypes=[("Super Tool Project Files", "*.pec")])
        if filename:
            p = stproject.Project()
            p.file_name = filename
            p.read_from_file_name()
            
            if not p.working_dir or not os.path.exists(p.working_dir):
                self.prompt_for_new_working_dir(proj=p)
            else:
                self.set_project(p)
            
    def set_project(self, proj):
        del self.project
        self.project = proj
        self.proj_frame.render()
        self.proj_frame.update_proj_header()
        self.focused_test = None
        self.test_frame.show_focused_test()
        self.param_frame.render()
        
    # method called in project view
    # shows a prompt for the user to rename the currently open project
    def rename_project(self, e=None):
        # entry popup
        new_project_name = simpledialog.askstring(title="Rename Project",
            prompt=f"Enter a new project name to replace\n{self.project.title}.")
        if new_project_name:
            # set the project name
            self.project.title = new_project_name
            
            # change project header in project pane
            self.proj_frame.update_proj_header()

    def prompt_for_new_working_dir(self, e=None, proj=None):
        
        print(proj.__repr__())
        print(self.project.__repr__())
        if proj == None:
            proj = self.project
        
        set_dir_window = BaseOkPopup(self, title="Choose a new working directory")
        
        dir_var = tk.StringVar(self, value=proj.working_dir)
        
        def dir_select():
            dirname = fd.askdirectory(mustexist=True, initialdir=self.project.working_dir)
            if dirname:
                # @TODO add a printout of the number of paths that are valid from
                # choosing a new directory. maybe add a verify button?
                dir_var.set(dirname)
        
        def ok_command(proj=proj):
            work_dir = dir_var.get()
            message_list = []
            
            if work_dir:
                if work_dir[-1] in '/\\':
                    work_dir = work_dir[:-1]
                
                if os.path.exists(work_dir):
                    # if it's not a directory, complain
                    if not os.path.isdir(work_dir):
                        message_list.append("The entered working directory is not a directory.")
                else:
                    message_list.append("The entered working directory does not exist.")
            else:
                message_list.append("Please enter a working directory for the project.")
        
            if message_list:
                # update the screen with errors
                set_dir_window.show_errors(message_list)
            else:
                set_dir_window.hide_errors()
            
                # close the new project window
                set_dir_window.destroy()
                
                print(proj.__repr__())
                print(self.project.__repr__())
                
                if work_dir != proj.working_dir:
                    proj.working_dir = work_dir
                    if proj != self.project:
                        self.set_project(proj)
                    # else:
                self.proj_frame.update_proj_header()
                if self.focused_test:
                    # rerender focused test to update hovertext @TODO do it better
                    self.test_frame.show_focused_test()
        
        def cancel_command():
            set_dir_window.destroy()
        
        dir_label = ttk.Label(set_dir_window.frame,
                text="Choose a new working directory. The project save file does not need\n" \
                   + "to be inside the working directory, but every file necessary\n" \
                   + "for PSLF (sav, dyd, csv) will need to be there.")
        dir_label.grid(row=0, column=0, sticky='w', columnspan=2)
        
        dir_entry = ttk.Entry(set_dir_window.frame, textvariable=dir_var, width=45)
        dir_entry.grid(row=1, column=0)
        
        dir_select_button = ttk.Button(set_dir_window.frame, text="Choose Folder",
                                       command=dir_select)
        dir_select_button.grid(row=1, column=1, sticky='ew')
        dir_select_button.bind("<Return>", lambda e: dir_select)
        
        set_dir_window.wrapup(ok_command=ok_command, cancel_command=cancel_command)

    # method called by ctrl+shift+s and the file menu
    # shows a prompt allowing the user to save to a pec file
    def save_project(self, e=None):
        if self.project.file_name:
            self.project.write_to_file_name()
        else:
            self.save_as_project()

    # method called by ctrl+shift+s and the file menu
    # shows a prompt allowing the user to save to a pec file
    def save_as_project(self, e=None):
        filename = fd.asksaveasfilename(defaultextension="*.*", filetypes=[("Super Tool Project Files", "*.pec")])
        if filename:
            self.project.file_name = filename
            self.project.write_to_file_name()
