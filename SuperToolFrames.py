# SuperToolFrames.py, Charlie Jordan, 11/17/2023
# where the frame classes for supertool live

import tkinter as tk
from tkinter import ttk
from superbackend import *
import SuperToolProject as stp
from SuperToolMenus import *

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
        self.parent.set_status("Status Bar: " + blah)

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
        
        menu = tk.Menu(self)
        for i in ('One', 'Two', 'Three'):
            menu.add_command(label=i)
        self.bind('<3>', lambda e: menu.post(e.x_root, e.y_root))

    def set_text(self, text):
        self.main_text.config(text=text)

class ScrollFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(parent, **kwargs)
        
        self.scrollbar = tk.Scrollbar(self, orient='vertical')
        self.scrollbar.pack(side='right', fill='y')
        
        
        self.canvas = tk.Canvas(self) #, background='#ffffff')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)
        
        self.frame = ttk.Frame(self.canvas, padding="0 0 4 0")
        self.canvas_frame = self.canvas.create_window((0,0), window=self.frame, anchor='nw')
        
        self.frame.bind("<Configure>", self.on_configure)
        self.canvas.bind('<Configure>', self.frame_width)
        
        self.frame.bind_all('<MouseWheel>', self.scroll_vertical)
        
        
    def scroll_vertical(self, e):
        xl = self.canvas.winfo_rootx()
        xr = xl + self.canvas.winfo_width() + self.scrollbar.winfo_width()
        yt = self.canvas.winfo_rooty()
        yb = yt + self.canvas.winfo_height()
        # print(xl, yt, "|", xr, yb)
        # print(self.canvas.winfo_pointerxy())
        
        x, y =self.canvas.winfo_pointerxy()
        if x > xl and x < xr and y > yt and y < yb:
            p = self.scrollbar.get()[0] + (-1*e.delta//120)*.05 # @TODO the .05 is a scrolling speed constant, change it
            self.canvas.yview_moveto(p)
        # self.canvas.yview_scroll(-1*e.delta//50, "units")
        
        
    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.reset_width()
    
    def frame_width(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def reset_width(self):
        if self.frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.frame.winfo_reqwidth())