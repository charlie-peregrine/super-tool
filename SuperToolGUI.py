# SuperToolGUI.py, Charlie Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import tkinter.filedialog  as fd

from superbackend import *
from SuperToolFrames import *
import SuperToolProject as stp

from ProjectView import ProjectView
from TestView import TestView
from PlotView import PlotView

from matplotlib import pyplot as plt

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
        self.project = stp.Project()
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
            plt.close('all')
            self.destroy()

        self.protocol('WM_DELETE_WINDOW', on_quit)
        

    # helper method to create and add all of the high level widgets to the 
    # main window. also handles making each row and column resize-able
    def widgets(self):
        # top bar menu setup
        self.menu()

        ### Frame creation
        # main frame setup, row and column configure for initial size and resizeability
        self.grid_rowconfigure(0, minsize=150, weight=1)
        self.grid_columnconfigure(0, minsize=50, weight=1)
        self.grid_rowconfigure(1, minsize=150, weight=1)
        self.grid_columnconfigure(1, minsize=50, weight=1)
        # self.grid_columnconfigure(2, minsize=50, weight=0)

        # create the sub-frames
        self.proj_frame = ProjectView(self)
        self.test_frame = TestView(self)
        # self.plot_frame = PlotView(self)
        self.param_frame = ParamView(self)
        self.statusbar_frame = StatusBar(self)


    # helper method to set up main window keybinds
    # @TODO check if these are still active in the plot popup
    def keybinds(self):
        self.bind("<F5>", self.test_frame.run_simulation)
        self.bind("<Control-o>", self.open_project)
        self.bind("<Control-s>", self.project.write_to_file_name)
        self.bind("<Control-S>", self.save_as_project)
        
    # helper method to set up the main file menu at the top of the
    # window
    def menu(self):
        # create and set menu as the applications titlebar menu
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        
        # sub-menu creation
        file_menu = tk.Menu(self.menubar)
        about_menu = tk.Menu(self.menubar)

        # add options to the file menu
        # accelerators don't actually do anything, they need to be set
        # in the keybinds method
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="ctrl+n") #@TODO make the accelerators do something
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator="ctrl+o")
        file_menu.add_command(label="Save Project", command=self.project.write_to_file_name, accelerator="ctrl+s")
        file_menu.add_command(label="Save Project As", command=self.save_as_project, accelerator="ctrl+shift+s")
        file_menu.add_separator()
        file_menu.add_command(label="New Unit", command=print)
        file_menu.add_command(label="New Test")
        file_menu.add_separator()
        file_menu.add_command(label="Open Workspace", command=open_workspace)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy)

        # add options to the about menu
        about_menu.add_command(label="About")
        about_menu.add_command(label="Version")
        
        # add the submenus to the menu bar
        self.menubar.add_cascade(label="File", menu=file_menu)
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
            self.project = stp.Project(new_project_name)
            # re-render project pane
            self.proj_frame.render()
            # clear test view
            self.focused_test = None
            self.test_frame.show_focused_test()
    
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

    # method called by ctrl+shift+s and the file menu
    # shows a prompt allowing the user to save to a pec file
    def save_as_project(self, e=None):
        filename = fd.asksaveasfilename(defaultextension="*.*", filetypes=[("Super Tool Project Files", "*.pec")])
        if filename:
            self.project.file_name = filename
            self.project.write_to_file_name()

# make the program run if it is called as the main python file
if __name__ == "__main__":
    gui = SuperToolGUI()
    gui.mainloop()
