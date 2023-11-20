# SuperToolFrames.py, Charlie Jordan, 11/17/2023
# where the frame classes for supertool live

import tkinter as tk
from tkinter import ttk

class ProjectView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                    height=300, width=300)
        self.grid(row=0,column=0, columnspan=1, rowspan=2, sticky="nesw")



        proj_header = ttk.Label(self, text="Project Name") # @TODO font size up
        proj_header.grid(row=0, column=0, columnspan=3, sticky='w')
        
        # example project tree text
        # would look a lot better with frames to hold the trees
        num_units = 3
        num_tests = 4
        line = 0
        for i in range(num_units):
            a = ttk.Label(self, text=("Unit " + str(i)))
            a.grid(row=1+line, column=0, padx=7, sticky='w')
            
            line += 1
            for j in range(num_tests):
                b = ttk.Label(self, text=("Test " + str(j)))
                b.grid(row=1+line, column=0, padx=14, sticky='w')
                line += 1
                
                c = ttk.Label(self, text=("load ref"))
                c.grid(row=1+line, column=0, padx=21, sticky='w')
                line += 1

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
        self.parent.statusbar_frame.set_text("Status Bar: " + blah)

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

    def set_text(self, text):
        self.main_text.config(text=text)

