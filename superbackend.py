# superbackend.py, Charlie Jordan, 11/16/2023
# backend code for the supertool gui, what all the buttons do

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askdirectory

# file picking:
# https://stackoverflow.com/questions/3579568/choosing-a-file-in-python-with-simple-dialog

def open_project():
    # filetypes section to pick a specific extension!
    filename = askopenfilename(filetypes=[("Python", "*.py")])
    print(filename)
    # do something else with the filename
    pass

def open_workspace():
    dirname = askdirectory()
    print(dirname)
    # do something else with the dirname
    pass