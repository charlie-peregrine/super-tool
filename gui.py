# gui.py, Charles Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import tkinter as tk
from tkinter import ttk

### Base window setup
root = tk.Tk()
root.title("Super Tool")

# remove the tear off option from the top menu bar
root.option_add('*tearOff', tk.FALSE)

# Allows the main frame to be resizeable with the window
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

### Top bar menu setup
menubar = tk.Menu(root)
root.config(menu=menubar)
file_menu = tk.Menu(menubar)

file_menu.add_command(label='Exit', command=root.destroy)
menubar.add_cascade(label="File", menu=file_menu)

### Frame creation
# main frame setup, row and column configure for initial size and resizeability
main_frame = ttk.Frame(root, height=600, width=600)
main_frame.grid_rowconfigure(0, minsize=200, weight=1)
main_frame.grid_columnconfigure(0, minsize=180, weight=1)
main_frame.grid_rowconfigure(1, minsize=200, weight=1)
main_frame.grid_columnconfigure(1,  minsize=250, weight=1)

# set up the sub-frames
proj_frame = ttk.Frame(main_frame, borderwidth=5, relief="ridge",
                       height=500, width=300)
test_frame = ttk.Frame(main_frame, borderwidth=5, relief="ridge",
                       height=100, width=300)
plot_frame = ttk.Frame(main_frame, borderwidth=5, relief="ridge",
                       height=100, width=300)
error_frame = ttk.Frame(main_frame) # nothing else so it's just a popup sort of deal

# place the frames in their grids, main_frame inside root and the rest
# inside main_frame
main_frame.grid(row=0,column=0, sticky="nesw")
proj_frame.grid(row=0,column=0,columnspan=1, rowspan=2, sticky="nesw")
test_frame.grid(row=0,column=1,columnspan=1, rowspan=1, sticky="nesw")
plot_frame.grid(row=1,column=1,columnspan=1, rowspan=1, sticky="nesw")
error_frame.grid(row=2, column=0, columnspan=2, sticky="nesw")

# example text inside the frames
proj_text = ttk.Label(proj_frame, text="project")
proj_text.grid(row=0,column=0)
test_text = ttk.Label(test_frame, text="test")
test_text.grid(row=0,column=0)
plot_text = ttk.Label(plot_frame, text="plot")
plot_text.grid(row=0,column=0)
error_text = ttk.Label(error_frame, text="Error Bar")
error_text.grid(row=0, column=0)


# # example button
# button = ttk.Button(mainframe, text="Hello")
# button.grid(column=1,row=1)

# label = ttk.Label(mainframe, text="What are frogs?")
# label.grid(column=2,row=2)

# # text box example
# username = StringVar()
# name = ttk.Entry(mainframe, textvariable=username)

# these 2 lines set the minimum size of the window to its initial size
# @TODO may need to mess with this later but it's fine for now
root.update()
root.minsize(root.winfo_width(), root.winfo_height())

root.mainloop()


# def calculate(*args):
#     try:
#         value = float(feet.get())
#         meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
#     except ValueError:
#         pass

# root = Tk()
# root.title("Feet to Meters")

# mainframe = ttk.Frame(root, padding="3 3 12 12")
# mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
# # root.columnconfigure(0, weight=1)
# # root.rowconfigure(0, weight=1)

# feet = StringVar()
# feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
# feet_entry.grid(column=2, row=1, sticky=(W, E))

# meters = StringVar()
# ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

# ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

# ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
# ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
# ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

# for child in mainframe.winfo_children(): 
#     child.grid_configure(padx=5, pady=5)

# feet_entry.focus()
# root.bind("<Return>", calculate)

# root.mainloop()