# SuperToolFrames.py, Charlie Jordan, 11/17/2023
# where the frame classes for supertool live

import tkinter as tk
from tkinter import ttk
from superbackend import *

try:
    from matplotlib.figure import Figure 
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    # from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
except:
    # @TODO add separate script to install needed packages
    print("Installing matplotlib")
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib" ])
    from matplotlib.figure import Figure 
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    
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
                            height=200, width=250)
        self.grid(row=0,column=2, columnspan=1, rowspan=2, sticky="nesw")
        
        fig = Figure(figsize=(5,5), dpi=100)
        y = [i**2 for i in range(101)]
        
        plot1 = fig.add_subplot(111)
        plot1.plot(y)
        
        canvas = FigureCanvasTkAgg(fig, master = self)
        canvas.get_tk_widget().pack() #(fill='both')
        

class StatusBar(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=2, relief='groove')
        self.grid(row=2, column=0, columnspan=3, sticky="nesw")

        
        self.main_text = ttk.Label(self, text="Status Bar")
        self.main_text.grid(row=0, column=0)
        
        self.button = ttk.Button(self, text="read proj", command=self.parent.project.read_from_file_name)
        self.button.grid(row=0, column=1, sticky='e')

    def set_text(self, text):
        self.main_text.config(text=text)

class ScrollFrame(tk.Frame):
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
        
        self.frame.bind_all('<MouseWheel>', self.scroll_vertical, add=True)
        
        
    def scroll_vertical(self, event):
        xl = self.canvas.winfo_rootx()
        xr = xl + self.canvas.winfo_width() + self.scrollbar.winfo_width()
        yt = self.canvas.winfo_rooty()
        yb = yt + self.canvas.winfo_height()
        # print(xl, yt, "|", xr, yb)
        # print(self.canvas.winfo_pointerxy())
        
        x, y =self.canvas.winfo_pointerxy()
        if x > xl and x < xr and y > yt and y < yb:
            p = self.scrollbar.get()[0] + (-1*event.delta//120)*.05 # @TODO the .05 is a scrolling speed constant, change it
            self.canvas.yview_moveto(p)
        # self.canvas.yview_scroll(-1*e.delta//50, "units")
        
        
    def scroll_to_top(self):
        self.canvas.yview_moveto(0)
    
    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.reset_width()
    
    def frame_width(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def reset_width(self):
        if self.frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.frame.winfo_reqwidth())
