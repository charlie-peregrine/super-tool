# gui.py, Charles Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import tkinter as tk
from tkinter import ttk
from superbackend import *

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
about_menu = tk.Menu(menubar)

file_menu.add_command(label="New")
file_menu.add_command(label="Open Project File")
file_menu.add_command(label="Open Workspace")
file_menu.add_separator()
file_menu.add_command(label='Exit', command=root.destroy)
menubar.add_cascade(label="File", menu=file_menu)

about_menu.add_command(label="About us")
about_menu.add_command(label="Version")
menubar.add_cascade(label="About", menu=about_menu)

### Frame creation
# main frame setup, row and column configure for initial size and resizeability
main_frame = ttk.Frame(root, height=600, width=600)
main_frame.grid_rowconfigure(0, minsize=150, weight=1)
main_frame.grid_columnconfigure(0, minsize=50, weight=1)
main_frame.grid_rowconfigure(1, minsize=150, weight=1)
main_frame.grid_columnconfigure(1, minsize=50, weight=1)
main_frame.grid_columnconfigure(2, minsize=50, weight=1)

# set up the sub-frames
proj_frame = ttk.Frame(main_frame, borderwidth=5, relief='groove',
                       height=300, width=300)
test_frame = ttk.Frame(main_frame, borderwidth=5, relief='groove',
                       height=100, width=100)
param_frame = ttk.Frame(main_frame, borderwidth=5, relief='groove',
                       height=100, width=100)
plot_frame = ttk.Frame(main_frame, borderwidth=5, relief='groove',
                       height=300, width=400)
statusbar_frame = ttk.Frame(main_frame, borderwidth=2, relief='groove') # nothing else so it's just a popup sort of deal

# place the frames in their grids, main_frame inside root and the rest
# inside main_frame
main_frame.grid(row=0,column=0, sticky="nesw")
proj_frame.grid(row=0,column=0, columnspan=1, rowspan=2, sticky="nesw")
test_frame.grid(row=0,column=1, columnspan=1, rowspan=1, sticky="nesw")
param_frame.grid(row=1,column=1, columnspan=1, rowspan=1, sticky="nesw")
plot_frame.grid(row=0,column=2, columnspan=1, rowspan=2, sticky="nesw")
statusbar_frame.grid(row=2, column=0, columnspan=3, sticky="nesw")

# example text inside the frames
# proj_text = ttk.Label(proj_frame, text="project")
# proj_text.grid(row=0,column=0)
# test_text = ttk.Label(test_frame, text="test")
# test_text.grid(row=0,column=0)
param_text = ttk.Label(param_frame, text="plot params")
param_text.grid(row=0,column=0)
statusbar_text = ttk.Label(statusbar_frame, text="Status Bar")
statusbar_text.grid(row=0, column=0)

### Project Frame Details
proj_header = ttk.Label(proj_frame, text="Project Name") # @TODO font size up
proj_header.grid(row=0, column=0, columnspan=3)
project_title = tk.StringVar()
proj_header_entry = ttk.Entry(proj_frame, textvariable=project_title)
proj_header_entry.grid(row=0,column=3, columnspan=2)

num_tests = 4
project_test_entries = [tk.StringVar() for i in range(num_tests)]
for i in range(num_tests):
    ttk.Label(proj_frame, text="Test %d\n  Test type" % (i+1)).grid(
        row=1+i, column=0, columnspan=2
    )
    ttk.Entry(proj_frame, textvariable=project_test_entries[i]).grid(
        row=1+i, column=2, columnspan=3
    )


### Test Parameters Box details
test_header = ttk.Label(test_frame, text="Test Parameters:") # @TODO font size up 
test_header.grid(row=0, column=0, columnspan=1, sticky="w")

def run_simulation(*args):
    blah = ' '.join([i.get() for i in strings])
    print(blah)
    statusbar_text.config(text="Status Bar: " + blah)

img = tk.PhotoImage(file="icons/supertoolplay.png")
ttk.Button(test_frame, image=img, command=run_simulation).grid(row=0, column=2)

# example input field to show that the entries work
strings = [tk.StringVar() for i in range(4)]

# example of fields, might be better as a class instead of a tuple 
lines = [("start time", strings[0], "sec"), ("end time", strings[1], "sec"),
         ("step up size", strings[2], "pu"), ("step down size", strings[3], "pu")]
for i in range(len(lines)):
    test_name = ttk.Label(test_frame, text=lines[i][0])
    test_input = ttk.Entry(test_frame, textvariable=lines[i][1], width=6)
    test_unit = ttk.Label(test_frame, text=lines[i][2])
    test_name.grid(row=2+i, column=0, sticky='w')
    test_input.grid(row=2+i, column=1)
    test_unit.grid(row=2+i, column=2)




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