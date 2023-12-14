# SuperToolFrames.py, Charlie Jordan, 11/17/2023
# where the frame classes for supertool live

import tkinter as tk
from tkinter import ttk

# import matplotlib
import matplotlib
# tell matplotlib to use the tkinter backend
matplotlib.use("TkAgg")

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

import numpy as np

class ParamView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                         height=100, width=100)
        self.grid(row=1,column=1, columnspan=1, rowspan=1, sticky="nesw")

        # param_text = ttk.Label(self, text="plot params")
        # param_text.grid(row=0,column=0)
        
        self.render_button = ttk.Button(self, text="Show Graphs",
                                        command=self.render)
        self.render_button.grid(row=0, column=0)

        self.graph_window = None
    
    def render(self):
        
        if self.graph_window:
            self.graph_window.destroy() # could be optimized by not destroying and instead replacing?
        
        self.graph_window = tk.Toplevel(self.parent)
        self.graph_window.title("Graph!")
        
        sim_file_name = r'C:\CODE\demo super tool gui\pslf_scripts\dump\HCPR3_VStepP02_P0_sim.csv'
        sim_array = np.genfromtxt(sim_file_name, delimiter=',', skip_header=True)
        real_time = sim_array[:, 0] - sim_array[0,0]
        # print(real_time)

        matplotlib.rcParams.update({'font.size': 8})

        fig, axs = plt.subplots(5, 1, figsize=(3.5,5), layout='constrained')

        axs[0].plot(real_time, sim_array[:, 1], label='sim') # vt 1
        axs[0].set_ylabel('Vt (kV)')
        axs[0].legend()

        axs[1].plot(real_time, sim_array[:, 5]) # pg 1
        axs[1].set_ylabel("P (MW)")

        axs[2].plot(real_time, sim_array[:, 7]) # qg 1
        axs[2].set_ylabel("Q (MVAR)")

        axs[3].plot(real_time, sim_array[:, 3], ) # efd 1
        axs[3].set_ylabel("Efd (VDC)")

        axs[4].plot(real_time, sim_array[:, 10])# ifd 1 ?
        axs[4].set_ylabel("Ifd (ADC)")
        axs[4].set_xlabel("Time (s)")

        fig.align_ylabels(axs)

        canvas = FigureCanvasTkAgg(fig, master = self.graph_window)
        canvas.get_tk_widget().pack(anchor="nw", fill='both', expand=1)
        
        def resize_canvas(e):
            if str(e.widget) == '.!toplevel':
                print(e, e.widget)
                if getattr(self, "_after_id", None):
                    self.graph_window.after_cancel(self._after_id)  # type: ignore
                if canvas.get_tk_widget().winfo_viewable():
                    canvas.get_tk_widget().pack_forget()
                self._after_id = self.graph_window.after(250,       # type: ignore
                    lambda: canvas.get_tk_widget().pack(
                        anchor="nw", fill='both', expand=1
                    )
                )
            
        self.graph_window.bind('<Configure>', resize_canvas)
        

class StatusBar(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=2, relief='groove')
        self.grid(row=2, column=0, columnspan=2, sticky="nesw")

        
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
