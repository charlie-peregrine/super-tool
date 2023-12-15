# TestView.py, Charlie Jordan, 12/5/2023
# file to store the gui work for the test pane of the UI

import tkinter as tk
import tkinter.ttk as ttk
from SuperToolFrames import ScrollFrame
from os.path import basename
from tkinter.filedialog import askopenfilename, asksaveasfilename
from idlelib.tooltip import Hovertip


# Frame subclass for presenting and receving info regarding
# individual tests and their attributes
class TestView(ttk.Frame):
    def __init__(self, parent):
        # set up the frame and place it in the window
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                            height=100, width=100)
        self.grid(row=0,column=1, columnspan=1, rowspan=1, sticky="nesw")
        
        ### Test Parameters Box details
        # header
        test_header = ttk.Label(self, text="Test Parameters:") # @TODO font size up 
        test_header.grid(row=0, column=0, columnspan=1, sticky="w")

        # run simulation button
        self.img = tk.PhotoImage(file="./icons/supertoolplay.png")
        self.run_button = ttk.Button(self, image=self.img, command=self.run_simulation)
        self.run_button.grid(row=0, column=2, sticky='ne')

        # Put a scroll frame in the frame
        self.scroller = ScrollFrame(self)
        self.frame = self.scroller.frame
        self.scroller.grid(row=1, column=0, columnspan=3, sticky='nesw')

        # make the applicable rows and columns resizable
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # show the focused test. note that when it's used in the initializer,
        # the "no test selected" text will always be shown since no test
        # is selected yet
        self.show_focused_test()
        

    # helper function to show the currently focused test in the test frame
    def show_focused_test(self):
        # empty the scroller's frame, deleting that frame is a bad idea
        # because of the specific configurations set in the ScrollFrame class
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # reset the scroller to the top of the frame
        # fixes a bug where when a large frame gets reset to a very small frame
        # the scrollbar would still act like the frame was large
        self.scroller.scroll_to_top()
        
        focused = self.parent.focused_test
        if focused: # if there is a focused test
            # put labels and buttons for the top of the scrollable frame
            self.title_label = ttk.Label(self.frame, text=focused.name)
            self.title_label.grid(row=0, column=0, sticky='w')
            self.type_label = ttk.Label(self.frame, text=focused.type)
            self.type_label.grid(row=1, column=0)
            # @TODO give the change type button an action
            self.type_button = ttk.Button(self.frame, text="change")
            self.type_button.grid(row=1, column=1, sticky='e')
            
            # set up for loop, offset is how many rows down the big
            # list of attributes should start
            keys = list(focused.attribute_dict.keys())
            offset = 2
            
            # storage for all of the interactibles so they still
            # work outside of the loop
            self.interactibles = []
            
            # for every attribute of the attribute dictionary, add
            # a line containing its name and relevant input fields
            for i in range(len(keys)):
                attr = focused.attribute_dict[keys[i]]
                
                # paths are shown with their name, their short name,
                # and a button to open a file picker window. hovering
                # over the short name shows a tooltip of the full path name
                if attr.type == 'PATH':
                    # attribute name shown
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    # show short name of path
                    path_label = ttk.Label(self.frame, text=basename(attr.var.get()))
                    path_label.grid(row=i+offset, column=1)
                    
                    # create hovertext for paths to show the long path instead of just the basename
                    path_label_hover = Hovertip(path_label, attr.var.get(), hover_delay=300)
                    
                    # set up traces for when the path variables update to modify the path label
                    # separate functions needed because lambdas don't allow assignments
                    attr.var.trace_add('write', lambda _1, _2, _3, l=path_label, v=attr.var: 
                                        l.configure(text=basename(v.get())))
                    def update_hover(_1, _2, _3, l=path_label_hover, v=attr.var):
                        l.text = v.get()
                    attr.var.trace_add('write', update_hover) 
                    
                    # place a select button to get new a new path
                    path_button = ttk.Button(self.frame, text="select",
                            command=lambda attr=attr: self.get_new_path(attr))
                    path_button.grid(row=i+offset, column=2)
                    
                    # add interactibles to a higher scoped list
                    self.interactibles.append((path_button, path_label))
                
                # boolean attributes are shown as their name and a checkbox
                elif attr.type == 'BOOL':
                    # attribute name shown
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    # show a check box
                    # @TODO the bind not be necessary
                    checkbutton = ttk.Checkbutton(self.frame, variable=attr.var)
                    checkbutton.bind("<1>", lambda e, var=attr.var: print(not var.get()))
                    checkbutton.grid(row=i+offset, column=1)
                    
                    # add the checkbox and variable to a higher scoped list
                    # @TODO is attr.var necessary here?
                    self.interactibles.append((checkbutton, attr.var))
                
                # if the attribute is a number, show it as a name, an entry, and
                # a unit @TODO error checking on the entry
                else:
                    # show the name
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    # space to enter the user's number
                    entry = ttk.Entry(self.frame, textvariable=attr.var)
                    entry.bind("<Return>", lambda e, var=attr.var: print(var.get()))
                    entry.grid(row=i+offset, column=1)
                    
                    # label containing unit
                    unit_label = ttk.Label(self.frame, text=attr.unit)
                    unit_label.grid(row=i+offset, column=2)
                    
                    # add the entry to a higher scoped list
                    # @TODO is attr.var necessary?
                    self.interactibles.append((entry, attr.var))
                
            
        else:
            # if there's no focused test, show that no test is selected
            # @TODO probably a memory leak due to dropping the old no_test_label
            self.no_test_label = ttk.Label(self.frame, text="No Test Selected. Create or click one to begin.")
            self.no_test_label.grid(row=1,column=0)
        
    # run the backend PSLF script associated with the focused test's
    # test type
    def run_simulation(self, *args):
        # print(self.parent.project)
        if self.parent.focused_test:
            self.parent.focused_test.script()
        else:
            # @TODO make this more elegant
            print("No focused test to run a script for!")
        # blah = ' '.join([i.get() for i in self.strings])
        # print(blah)
        # self.parent.set_status("Status Bar: " + blah)
    
    # get a new path for path type attributes
    # need to pick between input and output files because the file
    # picker has different behavior depending on if it's saving or
    # opening. uses tkinter.filedialog
    def get_new_path(self, attr):
        if attr.name[:3] in ('dyd', 'sav'):
            path = askopenfilename(title=f"Select {attr.name[:3]} file",
                                   defaultextension="*.*",
                                   filetypes=[("PSLF Input File", f"*.{attr.name[:3]}"),
                                              ("All Files", "*.*")]
                                   )
        else:
            path = asksaveasfilename(title=f"Choose file name and location for {attr.name[:3]} file",
                                     defaultextension="*.*",
                                     filetypes=[("PSLF Output File", f"*.{attr.name[:3]}"),
                                              ("All Files", "*.*")]
                                     )
        
        if path:
            attr.var.set(path)
