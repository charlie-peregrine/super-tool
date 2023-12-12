# TestView.py, Charlie Jordan, 12/5/2023
# file to store the gui work for the test pane of the UI

import tkinter as tk
import tkinter.ttk as ttk
from SuperToolFrames import ScrollFrame
from os.path import basename
from tkinter.filedialog import askopenfilename, asksaveasfilename
from idlelib.tooltip import Hovertip


class TestView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                            height=100, width=100)
        self.grid(row=0,column=1, columnspan=1, rowspan=1, sticky="nesw")
        
        ### Test Parameters Box details
        test_header = ttk.Label(self, text="Test Parameters:") # @TODO font size up 
        test_header.grid(row=0, column=0, columnspan=1, sticky="w")

        self.img = tk.PhotoImage(file="./icons/supertoolplay.png")
        self.run_button = ttk.Button(self, image=self.img, command=self.run_simulation)
        self.run_button.grid(row=0, column=2, sticky='ne')

        self.scroller = ScrollFrame(self)
        self.frame = self.scroller.frame
        self.scroller.grid(row=1, column=0, columnspan=3, sticky='nesw')

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.show_focused_test()
        

    def show_focused_test(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        self.scroller.scroll_to_top()
        
        focused = self.parent.focused_test
        if focused:
            self.title_label = ttk.Label(self.frame, text=focused.name)
            self.title_label.grid(row=0, column=0, sticky='w')
            self.type_label = ttk.Label(self.frame, text=focused.type)
            self.type_label.grid(row=1, column=0)
            self.type_button = ttk.Button(self.frame, text="change")
            self.type_button.grid(row=1, column=1, sticky='e')
            
            keys = list(focused.attribute_dict.keys())
            offset = 2
            
            self.interactibles = []
            
            for i in range(len(keys)):
                attr = focused.attribute_dict[keys[i]]
                # print(attr)
                if attr.type == 'PATH':
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    path_label = ttk.Label(self.frame, text=basename(attr.var.get()))
                    path_label.grid(row=i+offset, column=1)
                    
                    path_label_hover = Hovertip(path_label, attr.var.get(), hover_delay=300)
                    
                    attr.var.trace_add('write', lambda _1, _2, _3, l=path_label, v=attr.var: 
                                        l.configure(text=basename(v.get())))
                    
                    # separate functions needed because lambdas don't allow assignments
                    def update_hover(_1, _2, _3, l=path_label_hover, v=attr.var):
                        l.text = v.get()
                    attr.var.trace_add('write', update_hover) 
                    
                    
                    
                    path_button = ttk.Button(self.frame, text="select",
                            command=lambda attr=attr: self.get_new_path(attr))
                    path_button.grid(row=i+offset, column=2)
                    
                    self.interactibles.append((path_button, path_label))
                elif attr.type == 'BOOL':
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    checkbutton = ttk.Checkbutton(self.frame, variable=attr.var)
                    checkbutton.bind("<1>", lambda e, var=attr.var: print(not var.get()))
                    checkbutton.grid(row=i+offset, column=1)
                    
                    self.interactibles.append((checkbutton, attr.var))
                else:
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    entry = ttk.Entry(self.frame, textvariable=attr.var)
                    entry.bind("<Return>", lambda e, var=attr.var: print(var.get()))
                    entry.grid(row=i+offset, column=1)
                    
                    unit_label = ttk.Label(self.frame, text=attr.unit)
                    unit_label.grid(row=i+offset, column=2)
                    
                    self.interactibles.append((entry, attr.var))
                
            
        else:
            # @TODO prolly a memory leak
            self.no_test_label = ttk.Label(self.frame, text="No Test Selected. Create or click one to begin.")
            self.no_test_label.grid(row=1,column=0)
        
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
        