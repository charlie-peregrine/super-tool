# SuperToolFrames.py, Charlie Jordan, 11/17/2023
# where the frame classes for supertool live

import tkinter as tk
from tkinter import ttk

# the statusbar frame should hold details about current background tasks
# happening, such as loading times, file opening and closing info,
# and other info that is relevant to the whole application and can be presented
# as out of the way text
class StatusBar(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=2, relief='groove')

        
        self.main_text = ttk.Label(self, text="Status Bar")
        self.main_text.grid(row=0, column=0)

    # helper method to let other methods easily set the status bar's main
    # text field
    def set_text(self, text):
        self.main_text.config(text=text)


# A multiple use scrollbar frame
# the .frame frame is the one to place other widgets into,
# as the other parts should not be modified outside of this class
class ScrollFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        # set parent and use the frame superclasses initialization
        self.parent = parent
        super().__init__(parent, **kwargs)
        
        # add a vertical scrollbar and put it in the main frame
        self.scrollbar = tk.Scrollbar(self, orient='vertical')
        self.scrollbar.pack(side='right', fill='y')
        
        # put a canvas in the main frame as well
        self.canvas = tk.Canvas(self) #, background='#ffffff')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # set the canvas to scroll with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)
        
        # add a frame for other widgets to be placed in.
        # the frame is added to the canvas as a window to
        # make it scrollable inside of the canvas
        self.frame = ttk.Frame(self.canvas, padding="0 0 4 0")
        self.canvas_frame = self.canvas.create_window((0,0), window=self.frame, anchor='nw')
        
        # when the frame holding the canvas and frame is resized,
        # change the sizes of them accordingly 
        self.frame.bind("<Configure>", self.on_configure)
        self.canvas.bind('<Configure>', self.frame_width)
        
        # let the user scroll while inside the editable frame, not just the scrollbar
        self.frame.bind_all('<MouseWheel>', self.scroll_vertical, add=True)
        
    # command used to properly scroll vertically in any ScrollFrame
    def scroll_vertical(self, event):
        # calculations used to check if the pointer is inside the canvas
        xl = self.canvas.winfo_rootx()
        xr = xl + self.canvas.winfo_width() + self.scrollbar.winfo_width()
        yt = self.canvas.winfo_rooty()
        yb = yt + self.canvas.winfo_height()
        # print(xl, yt, "|", xr, yb)
        # print(self.canvas.winfo_pointerxy())
        
        # if the pointer is inside the canvas...
        x, y = self.canvas.winfo_pointerxy()
        if x > xl and x < xr and y > yt and y < yb:
            # move the canvas accordingly
            # @TODO the .05 is a scrolling speed constant, change it maybe
            p = self.scrollbar.get()[0] + (-1*event.delta//120)*.05
            self.canvas.yview_moveto(p)
        # self.canvas.yview_scroll(-1*e.delta//50, "units")
        
    # reset the scrollframe by moving the canvas to the top of its available space
    def scroll_to_top(self):
        self.canvas.yview_moveto(0)
    
    ## all 3 of the following are necessary, though the last one could be 
    ## merged into on_configure instead of being a separate method
    ## @TODO make better comments for this section
    # helper command to resize the canvas and scrollable region appropriately
    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.reset_width()
    
    # helper command to resize the canvas and scrollable region appropriately
    def frame_width(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    # helper command to resize the canvas and scrollable region appropriately
    def reset_width(self):
        if self.frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.frame.winfo_reqwidth())
