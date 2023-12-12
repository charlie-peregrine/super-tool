# SuperToolGUI.py, Charlie Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from superbackend import *
from SuperToolFrames import *
import SuperToolProject as stp
import tkinter.filedialog  as fd

from ProjectView import ProjectView
from TestView import TestView

class SuperToolGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        ### setup root window options
        self.title("Super Tool")
        # remove the tear off option from the top menu bar
        self.option_add('*tearOff', tk.FALSE)
        # Allows the main frame to be resizeable with the window
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.project = stp.Project()
        self.focused_test = None
        
        self.widgets()
        self.keybinds()
        
        # these 2 lines set the minimum size of the window to its initial size
        # @TODO may need to mess with this later but it's fine for now
        self.update()
        self.minsize(500,250)
        # print(self.winfo_width(), self.winfo_height())
        

    def widgets(self):

        ### Top bar menu setup
        self.menu()

        ### Frame creation
        # main frame setup, row and column configure for initial size and resizeability
        self.grid_rowconfigure(0, minsize=150, weight=1)
        self.grid_columnconfigure(0, minsize=50, weight=1)
        self.grid_rowconfigure(1, minsize=150, weight=1)
        self.grid_columnconfigure(1, minsize=50, weight=1)
        self.grid_columnconfigure(2, minsize=50, weight=1)

        # set up the sub-frames
        self.proj_frame = ProjectView(self)
        self.test_frame = TestView(self)
        self.param_frame = ParamView(self)
        self.plot_frame = PlotView(self)
        self.statusbar_frame = StatusBar(self)


    def keybinds(self):
        self.bind("<F5>", self.test_frame.run_simulation)
        self.bind("<Control-o>", self.open_project)
        self.bind("<Control-s>", self.project.write_to_file_name)
        self.bind("<Control-S>", self.save_as_project)
        
    def menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar)
        about_menu = tk.Menu(self.menubar)

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

        about_menu.add_command(label="About us")
        about_menu.add_command(label="Version")
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menubar.add_cascade(label="About", menu=about_menu)
    
    def set_status(self, string):
        self.statusbar_frame.set_text(string)
    
    def new_project(self, e=None):
        # confirmation popup
        # @TODO make this a string input for a new project name
        new_project_name = simpledialog.askstring(title="New Project", 
            prompt="Enter a name for the new project.\nAll unsaved progress will be lost.")
        if new_project_name:
            # delete current project class
            del self.project
            self.project = stp.Project(new_project_name)
            # re-render project pane
            self.proj_frame.render()
            self.focused_test = None
            # clear test view
            self.test_frame.show_focused_test()
    
    def open_project(self, e=None):
        filename = fd.askopenfilename(filetypes=[("Super Tool Project Files", "*.pec")])
        if filename:
            self.project.file_name = filename
            self.project.read_from_file_name()
            self.proj_frame.render()
            self.focused_test = None
            self.test_frame.show_focused_test()

    def save_as_project(self, e=None):
        filename = fd.asksaveasfilename(defaultextension="*.*", filetypes=[("Super Tool Project Files", "*.pec")])
        if filename:
            # if '.' not in filename:
            self.project.file_name = filename
            self.project.write_to_file_name()

if __name__ == "__main__":
    gui = SuperToolGUI()
    gui.mainloop()
