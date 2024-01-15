# ParamView.py, Charlie Jordan, 1/12/2024
# Graph Parameter modification pane of the main supertool gui window

import tkinter as tk
from tkinter import ttk

from SuperToolFrames import ScrollFrame

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
    
        # self.scroller = ScrollFrame(self)
        # self.scroll_frame = self.scroller.frame
    
        self.blobs = []
        for i in range(4):
            l = ttk.Label(self, text="hey " + str(i))
            l.grid(row=1+i, column=0)
            self.blobs.append(l)
            
            e1 = ttk.Entry(self)
            e1.grid(row=1+i, column=1)
            self.blobs.append(e1)
            
            e2 = ttk.Entry(self)
            e2.grid(row=1+i, column=2)
            self.blobs.append(e2)
            
    def render(self):
        
        if not self.parent.focused_test:
            print("no focused test yet")
            return
        
        self.parent.focused_test.plot()
        
        
        