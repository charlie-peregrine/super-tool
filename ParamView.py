# ParamView.py, Charlie Jordan, 1/12/2024
# Graph Parameter modification pane of the main supertool gui window

import tkinter as tk
from tkinter import ttk

import veusz_handler

# subclass of frame that holds the plot parameter view
# the goal of this view is to allow the user to manipulate
# the plotted graphs to be more visually appealing in order
# to make sense as graph objects
# currently a WIP  
class ParamView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                         height=100, width=100)

        # param_text = ttk.Label(self, text="plot params")
        # param_text.grid(row=0,column=0)
        
        self.render_button = ttk.Button(self, text="Show Graphs",
                                        command=self.render)
        self.render_button.grid(row=0, column=0)

        self.graph_window = None
    
    def render(self):
        
        if not self.parent.focused_test:
            print("no focused test yet")
            return
        
        veusz_handler.plot_voltage_reference(
            sim_file=self.parent.focused_test['csv_filename'],
            mes_file=self.parent.focused_test['mes_filename']
        )
        
        