# TestView.py, Charlie Jordan, 12/5/2023
# file to store the gui work for the test pane of the UI

import tkinter as tk
import tkinter.ttk as ttk

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

        self.frame = tk.Frame(self, background='white')
        self.frame.grid(row=1, column=0, columnspan=3, sticky='nesw')

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.show_focused_test()
        

    def show_focused_test(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
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
                attribute = keys[i]
                val, type_ = focused.attribute_dict[attribute]
                print(attribute, val, type_, sep='\t\t')
                if type_ == 'PATH':
                    pass # do path stuff
                    a = ttk.Label(self.frame, text=attribute)
                    a.grid(row=i+offset, column=0, sticky='w')
                    b = ttk.Label(self.frame, text=val)
                    b.grid(row=i+offset, column=1)
                    c = ttk.Button(self.frame, text="select", command=lambda: print('gwa'))
                    c.grid(row=i+offset, column=2)
                    self.interactibles.append(c)
                elif type_ == 'BOOL':
                    pass # checkbox
                    a = ttk.Label(self.frame, text=attribute)
                    a.grid(row=i+offset, column=0, sticky='w')
                    tk_val = tk.BooleanVar(value=val)
                    b = tk.Checkbutton(self.frame, variable=tk_val)
                    b.grid(row=i+offset, column=1)
                    if val:
                        b.select()
                    self.interactibles.append((b, tk_val))
                else:
                    # number time
                    a = ttk.Label(self.frame, text=attribute)
                    a.grid(row=i+offset, column=0, sticky='w')
                    # b = ttk.Label(self.frame, text=val)
                    # b.grid(row=i+offset, column=1)
                    d = tk.DoubleVar(value=val)
                    c = ttk.Entry(self.frame, textvariable=d)
                    c.grid(row=i+offset, column=1)
                    self.interactibles.append((c, d))
                
            
        else:
            self.grabo = ttk.Label(self.frame, text="No Test Selected. Create or click one to begin.")
            self.grabo.grid(row=1,column=0)

    def run_simulation(self, *args):
        pass
        # blah = ' '.join([i.get() for i in self.strings])
        # print(blah)
        # self.parent.set_status("Status Bar: " + blah)