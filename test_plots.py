# test_plots.py, Charlie Jordan, 12/13/2023
# test script to figure out matplotlib

import tkinter as tk

import numpy as np

import matplotlib
matplotlib.use("TkAgg")

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()

sim_file_name = r'C:\CODE\demo super tool gui\pslf_scripts\dump\HCPR3_VStepP02_P0_sim.csv'
sim_array = np.genfromtxt(sim_file_name, delimiter=',', skip_header=True)
real_time = sim_array[:, 0] - sim_array[0,0]
# print(real_time)

x = np.linspace(0, 2, 100)

fig, axs = plt.subplots(5, 1, figsize=(8,5), layout='constrained')

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

canvas = FigureCanvasTkAgg(fig, master = root)
canvas.get_tk_widget().pack(fill='both', expand=1)

def on_quit():
    plt.close('all')
    root.destroy()

root.protocol('WM_DELETE_WINDOW', on_quit)
root.mainloop()

