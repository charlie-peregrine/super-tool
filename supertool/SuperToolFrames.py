# SuperToolFrames.py, Charlie Jordan, 11/17/2023
# where the frame classes for supertool live

import tkinter as tk
import tkinter.font
from tkinter import ttk
from collections import deque

# the statusbar frame should hold details about current background tasks
# happening, such as loading times, file opening and closing info,
# and other info that is relevant to the whole application and can be presented
# as out of the way text
class StatusBar(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=2, relief='groove') #, background='red')

        self.columnconfigure(1, weight=1)
        
        initial_text = "Loading Super Tool..."
        self.history = deque([initial_text], maxlen=10)
        
        self.main_text = ttk.Label(self, text=initial_text)
        self.main_text.grid(row=0, column=1, sticky='w')
        
        self.history_button = ttk.Button(self, text="History",
                command=self.show_history)
        self.history_button.grid(row=0, column=2, sticky='e')
        
        self.spinner = SpinnerLabel(self, ms_delay=250)
        self.spinner.grid(row=0, column=0, sticky='w')
        
        style = ttk.Style()
        
        # create style for path buttons with paths that don't exist 
        font = tkinter.font.nametofont(style.lookup('TLabel', 'font'))
        style.configure('ErrorLabel.TLabel', foreground='red',
            font=(font.cget('family'), font.cget('size'), 'bold'))
        

    # helper method to let other methods easily set the status bar's main
    # text field
    def set_text(self, text, error=False, spin=False):
        self.history.append(text)
        
        if error:
            self.main_text.config(style='ErrorLabel.TLabel',
                text="ERROR: " + text)
        else:
            self.main_text.config(text=text, style='TLabel')
        
        if spin:
            self.spinner.start()
            self.spinner.grid()
        else:
            self.spinner.grid_remove()
            self.spinner.stop()
    
    def show_history(self):
        hist_window = Popup(self.parent, "Status Bar History", force=False)
        sep = ''
        for i, line in enumerate(self.history, start=1):
            if i >= len(self.history):
                sep = '>'
            print(i, sep, line)
            label = ttk.Label(hist_window, text=f"{sep:<1} {i:<2} {line}", style="Spinner.TLabel")
            label.grid(row=i, column=0, sticky='w', padx=5)

class SpinnerLabel(ttk.Label):
    chars = "|/-\\"
    length = len(chars)
    
    def __init__(self, parent, ms_delay=250, **kwargs):
        super().__init__(parent, style="Spinner.TLabel", **kwargs)
        
        self.ms_delay = ms_delay
        self.index = 0
        
        self.config(text=SpinnerLabel.chars[self.index])
        
        self.after_code = ""
        
        style = ttk.Style(self)
        font = tkinter.font.nametofont('TkFixedFont')
        style.configure('Spinner.TLabel', font=font)
        self.start()
    
    def next(self):
        self.index = (self.index + 1) % SpinnerLabel.length
        self.config(text=SpinnerLabel.chars[self.index])
        self.after_code = self.after(self.ms_delay, self.next)
    
    def start(self):
        if not self.after_code:
            self.next()
    
    def stop(self):
        if self.after_code:
            self.after_cancel(self.after_code)
            self.after_code = ""

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
        try:
            widg = self.canvas.winfo_containing(x, y)
        except KeyError:
            return
        if xr > x > xl and yb > y > yt and str(widg).startswith(str(self.frame)):
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

# Base popup class for super tool.
class Popup(tk.Toplevel):
    def __init__(self, root=None, title="Popup", *, force=True, **kwargs):
        super().__init__(root, **kwargs)
        # grab and hold focus
        self.transient(root)
        if force:
            self.grab_set()
            self.focus_force()
        
        # set window title, size, and resizability
        self.title(title)
        # find where to put the window, trying to center
        x_point = root.winfo_rootx() + root.winfo_width()//5
        y_point = root.winfo_rooty() + root.winfo_height()//5
        self.geometry(f"+{x_point}+{y_point}")
        self.resizable(False, False)

class BaseOkPopup(Popup):
    def __init__(self, root=None, title="Popup"):
        super().__init__(root, title)

        self.frame = ttk.Frame(self)
        self.frame.grid(row=0, column=0, sticky='nesw')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.grid(row=1, column=0, sticky='ew')
        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=1)
        
        self.error_sep = ttk.Separator(self.bottom_frame)
        self.error_sep.grid(row=0, column=0, columnspan=3, sticky='ew')
        self.error_sep.grid_remove()
        self.error_label = ttk.Label(self.bottom_frame, text="error_label")
        self.error_label.grid(row=1, sticky='nesw', padx=2, pady=2)
        self.error_label.grid_remove()
        
        self.sep = ttk.Separator(self.bottom_frame)
        self.sep.grid(row=2, column=0, columnspan=3, sticky='ew')
        self.ok_button = ttk.Button(self.bottom_frame, text="OK")
        self.ok_button.grid(row=3, column=1, sticky='e', padx=2, pady=2)
        self.cancel_button = ttk.Button(self.bottom_frame, text="Cancel")
        self.cancel_button.grid(row=3, column=2, sticky='e', padx=2, pady=2)
        
    def wrapup(self, ok_command, cancel_command):
        for widget in self.frame.winfo_children():
            widget.grid_configure(padx=2, pady=2)
        
        self.ok_button.config(command=ok_command)
        self.ok_button.bind("<Return>", lambda e: ok_command)
        
        self.cancel_button.config(command=cancel_command)
        self.cancel_button.bind("<Return>", lambda e: cancel_command)
        
        self.protocol("WM_DELETE_WINDOW", cancel_command)
        self.master.wait_window(self)

    def show_errors(self, error_list: list[str] = []):
        """
        Show the error label and separator, and fill it with newline separated
        elements or error_list. If error_list is empty, the error label is hidden
        """
        if error_list:
            self.error_label.config(text="\n".join(error_list))
            self.error_label.grid()
            self.error_sep.grid()
        else:
            self.error_label.grid_remove()
            self.error_sep.grid_remove()
        
    
    def hide_errors(self):
        self.error_label.grid_remove()
        self.error_sep.grid_remove()
