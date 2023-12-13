# PlotView.py, Charlie Jordan, 12/13/2023
# a subframe of the supertool application that holds the plots of
# simulations

import tkinter as tk
from tkinter import ttk

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
        
