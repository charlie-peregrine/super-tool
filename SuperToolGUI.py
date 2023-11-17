# SuperToolGUI.py, Charlie Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import tkinter as tk
from tkinter import ttk
from superbackend import *
from SuperToolFrames import *

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

        self.widgets()
        self.keybinds()
        
        # these 2 lines set the minimum size of the window to its initial size
        # @TODO may need to mess with this later but it's fine for now
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

    def widgets(self):

        ### Top bar menu setup
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        about_menu = tk.Menu(menubar)

        file_menu.add_command(label="New", accelerator="ctrl+n") #@TODO make the accelerators do something
        file_menu.add_command(label="Save", accelerator="ctrl+s")
        file_menu.add_command(label="Save As", command=save_as_project, accelerator="ctrl+shift+s")
        file_menu.add_command(label="Open Project File", command=open_project)
        file_menu.add_command(label="Open Workspace", command=open_workspace)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        about_menu.add_command(label="About us")
        about_menu.add_command(label="Version")
        menubar.add_cascade(label="About", menu=about_menu)

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


if __name__ == "__main__":
    gui = SuperToolGUI()
    gui.mainloop()
