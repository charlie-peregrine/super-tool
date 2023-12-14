# PlotView.py, Charlie Jordan, 12/13/2023
# a subframe of the supertool application that holds the plots of
# simulations

import tkinter as tk
from tkinter import ttk

# @TODO add separate script to install needed packages
# try:
# except:
#     print("Installing matplotlib")
#     import subprocess, sys
#     subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib" ])
#     import matplotlib


# import matplotlib
import matplotlib
# tell matplotlib to use the tkinter backend
matplotlib.use("TkAgg")

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

import numpy as np
    


class PlotView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                            height=200, width=250)
        self.grid(row=0,column=2, columnspan=1, rowspan=2, sticky="nesw")
        
    def render(self):
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

        RENDER_AS_IMAGE = False

        if RENDER_AS_IMAGE:
            fig.savefig('blah.png')
            self.pic = tk.PhotoImage(file="blah.png")
            self.label = ttk.Label(self, image=self.pic)
            self.label.pack(fill="both", expand=1)
        else:
            canvas = FigureCanvasTkAgg(fig, master = self)
            canvas.get_tk_widget().pack(anchor="nw") #fill='both', expand=1)

        
