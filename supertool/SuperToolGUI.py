# SuperToolGUI.py, Charlie Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import tkinter.filedialog  as fd

import supertool.consts as consts
from supertool.SuperToolFrames import *
import supertool.SuperToolProject.Project as stproject

from supertool.ProjectView import ProjectView
from supertool.TestView import TestView
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
        
        # run the helper methods to set up widgets and full window keybinds
        self.widgets()
        self.keybinds()
        
        # these 2 lines set the minimum size of the window to its initial size
        # @TODO may need to mess with this later but it's fine for now, is update necessary?
        self.update()
        self.minsize(500,250)
        # print(self.winfo_width(), self.winfo_height())
        
        def on_quit():
            self.destroy()

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
        self.run_menu.add_command(
            label="Run",
            command=self.test_frame.run_simulation,
            accelerator="F5")
        self.run_menu.add_command(
            label="Run Without Saving",
            command=lambda: self.test_frame.run_simulation(
                save_on_run=False
            ),
            accelerator="ctrl+F5")

        # add options to the about menu
        about_menu.add_command(label="About")
        about_menu.add_command(label="Version")
        
        # add the submenus to the menu bar
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menubar.add_cascade(label="Run", menu=self.run_menu)
        self.menubar.add_cascade(label="About", menu=about_menu)
    
    # wrapper for statusbar text setting
    # needs some work
    def set_status(self, string):
        self.statusbar_frame.set_text(string)
    
    # method called by ctrl+n and the file menu
    # shows a prompt asking for a new file name and
    # creates a new project
    # @TODO make the prompt a custom window and institute some error checking
    def new_project(self, e=None):
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
    
    # method called by ctrl+o and the file menu
    # shows a prompt allowing the user to select a pec file to open
    # then opens the file
    def open_project(self, e=None):
        filename = fd.askopenfilename(filetypes=[("Super Tool Project Files", "*.pec")])
        if filename:
            self.project.file_name = filename
            self.project.read_from_file_name()
            self.proj_frame.render()
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
