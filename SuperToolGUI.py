# SuperToolGUI.py, Charlie Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import tkinter as tk
from tkinter import ttk
from superbackend import *


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

        # these 2 lines set the minimum size of the window to its initial size
        # @TODO may need to mess with this later but it's fine for now
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

    def keybinds(self):
        self.bind("<F5>", self.test_frame.run_simulation)

class ProjectView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                    height=300, width=300)
        self.grid(row=0,column=0, columnspan=1, rowspan=2, sticky="nesw")

        proj_header = ttk.Label(self, text="Project Name") # @TODO font size up
        proj_header.grid(row=0, column=0, columnspan=3)
        project_title = tk.StringVar()
        proj_header_entry = ttk.Entry(self, textvariable=project_title)
        proj_header_entry.grid(row=0,column=3, columnspan=2)

        num_tests = 4
        project_test_entries = [tk.StringVar() for i in range(num_tests)]
        for i in range(num_tests):
            ttk.Label(self, text="Test %d\n  Test type" % (i+1)).grid(
                row=1+i, column=0, columnspan=2
            )
            ttk.Entry(self, textvariable=project_test_entries[i]).grid(
                row=1+i, column=2, columnspan=3
            )

class TestView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                            height=100, width=100)
        self.grid(row=0,column=1, columnspan=1, rowspan=1, sticky="nesw")
        
        ### Test Parameters Box details
        test_header = ttk.Label(self, text="Test Parameters:") # @TODO font size up 
        test_header.grid(row=0, column=0, columnspan=1, sticky="w")

        self.img = tk.PhotoImage(file="./icons/supertoolplay.png")
        ttk.Button(self, image=self.img, command=self.run_simulation).grid(row=0, column=2)

        # example input field to show that the entries work
        self.strings = [tk.StringVar() for i in range(4)]

        # example of fields, might be better as a class instead of a tuple 
        lines = [("start time", self.strings[0], "sec"), ("end time", self.strings[1], "sec"),
                ("step up size", self.strings[2], "pu"), ("step down size", self.strings[3], "pu")]
        for i in range(len(lines)):
            test_name = ttk.Label(self, text=lines[i][0])
            test_input = ttk.Entry(self, textvariable=lines[i][1], width=6)
            test_unit = ttk.Label(self, text=lines[i][2])
            test_name.grid(row=2+i, column=0, sticky='w')
            test_input.grid(row=2+i, column=1)
            test_unit.grid(row=2+i, column=2)

    def run_simulation(self, *args):
        blah = ' '.join([i.get() for i in self.strings])
        print(blah)
        self.parent.statusbar_frame.main_text.config(text="Status Bar: " + blah)

class ParamView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                         height=100, width=100)
        self.grid(row=1,column=1, columnspan=1, rowspan=1, sticky="nesw")

        param_text = ttk.Label(self, text="plot params")
        param_text.grid(row=0,column=0)

class PlotView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                            height=300, width=400)
        self.grid(row=0,column=2, columnspan=1, rowspan=2, sticky="nesw")

class StatusBar(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=2, relief='groove')
        self.grid(row=2, column=0, columnspan=3, sticky="nesw")

        
        self.main_text = ttk.Label(self, text="Status Bar")
        self.main_text.grid(row=0, column=0)

if __name__ == "__main__":
    gui = SuperToolGUI()
    gui.mainloop()


# root.bind("<Return>", calculate)

# root.mainloop()