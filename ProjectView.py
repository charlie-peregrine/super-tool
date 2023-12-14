# ProjectView.py, Charlie Jordan, 11/28/2023
# Contains the frame for the project panel and
# all of its derivatives


import tkinter as tk
from tkinter import ttk
from SuperToolFrames import ScrollFrame
# @TODO replace messagebox and simpledialog with more robust windows
from tkinter import messagebox
from tkinter import simpledialog
from SuperToolProject import Attribute

class ProjectView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                    height=300, width=300)
        self.grid(row=0,column=0, columnspan=1, rowspan=2, sticky="nesw")

        self.proj = parent.project

        # the row and column configures allow for the scrollbar
        # frame and label section to resize correctly
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        # @TODO font size up of header
        self.proj_header = ttk.Label(self, text=self.proj.title)
        self.proj_header.grid(row=0, column=0, columnspan=3, sticky='w')
        
        self.scroller = ScrollFrame(self)
        self.scroller.grid(row=1, column=0, sticky='nesw')
        # self.blog = tk.Frame(self, background='red')
        # self.blog.grid(row=0, column=0, sticky='nesw')
        
        # a = stp.Unit()
        # b = stp.Unit()
        # a.test_dict = {-1 : stp.Test(), 1 : stp.Test()}
        # b.test_dict = {3 : stp.Test(), 2 : stp.Test(), 4 : stp.Test()}
        # b.name = "Unit AAAAAAAAAAAAAAAAAAA"
        # proj.unit_list = [a] #,b, stp.Unit(), b, a, a]
        
        # self.proj.add_unit("Example Unit!!!")
        # self.proj["Example Unit!!!"].add_test("test one", "load ref")
        # self.proj["Example Unit!!!"].add_test("test two", "load ref")
        # self.proj["Example Unit!!!"].add_test("test three", "load ref")
        # self.proj["Example Unit!!!"].add_test("test four", "load ref")
        # self.proj["Example Unit!!!"].add_test("test five", "load ref")
        # # self.proj["Example Unit!!!"].add_test("second test", "dynamic")
        # self.proj.add_unit("Second Unit")
        # self.proj.add_unit("3 U")
        # self.proj.add_unit("AAAAAAAAAAAAA")
        # u = self.proj["Second Unit"]
        # u.add_test("Idaho test 3", "Voltage Reference")
        # u.add_test("4000", "Evil Test Type >:)")
        # u.tests["Idaho test 3"].attribute_dict = {
        #     "dyd_filename" : Attribute("dyd_filename", "HCPR1.dyd", 'PATH'),
        #     "sav_filename" : Attribute("sav_filename", "HCPR1_VR_P0_new.sav", 'PATH'),
        #     "chf_filename" : Attribute("chf_filename", "HCPR1_VR_P0_new_sim.chf", 'PATH'),
        #     "csv_filename" : Attribute("csv_filename", "HCPR1_VR_P0_new_sim.csv", 'PATH'),
        #     "rep_filename" : Attribute("rep_filename", "Rep.rep", 'PATH'),
        #     "StepTimeInSecs"    : Attribute("StepTimeInSecs", 1.7, ''),
        #     "UpStepInPU"        : Attribute("UpStepInPU", 0.02, ''),
        #     "DnStepInPU"        : Attribute("DnStepInPU", 0.02, ''),
        #     "StepLenInSecs"     : Attribute("StepLenInSecs", 9.0, ''),
        #     "TotTimeInSecs"     : Attribute("TotTimeInSecs", 15, ''),
        #     "PSS_On"            : Attribute("PSS_On", True, 'BOOL'),
        #     "SysFreqInHz"       : Attribute("SysFreqInHz", 60.00, ''),
        #     "SimPtsPerCycle"    : Attribute("SimPtsPerCycle", 8.0, ''),
        #     "set_loadflow"      : Attribute("set_loadflow", False, 'BOOL'),
        #     "save_loadflow"     : Attribute("save_loadflow", False, 'BOOL'),
        #     # loadflow Parameters
        #     "Pinit"     : Attribute("Pinit", 118.85, ''),  # MW
        #     "Qinit"     : Attribute("Qinit", -1.98, ''),  # MVAR
        #     "MVAbase"   : Attribute("MVAbase", 145.0, ''),
        #     "Vinit"     : Attribute("Vinit", 14.585, ''),  # kV,
        #     "Vbase"     : Attribute("Vbase", 14.5, ''),   # kV,
        #     # "Zbranch"   : Attribute("Zbranch", 0.09, ''),  # pu
        # }
        
        self.dummy_label = ttk.Label(self)
        
        self.render()
        
    def render(self):
        
        # reset self.proj in case the project object got changed
        self.proj = self.parent.project
        
        # keep the visible project tile up to date
        self.proj_header.config(text=self.proj.title)
        
        frame = self.scroller.frame
        # clear the scroller frame if there's anything in it
        for widget in frame.winfo_children():
            widget.destroy()
        
        self.clicked_widget = self.dummy_label
        
        if self.proj.units:
            for unit_key in sorted(self.proj.units.keys()):
                
                unit = self.proj.units[unit_key]
                sep = ttk.Separator(frame, orient='horizontal')
                sep.pack(fill='x')
                
                unit_frame = ttk.Frame(frame, padding='10 0 0 4')
                unit_frame.pack(fill='x')
                
                unit_label = ttk.Label(unit_frame, text=unit.name)
                unit_label.pack(anchor='w')

                unit_label_menu = tk.Menu(unit_label)
                def right_click_unit(e):
                    self.clicked_widget = e.widget
                    unit_label_menu.post(e.x_root, e.y_root)
                
                unit_label.bind("<3>", lambda e: right_click_unit(e))
                unit_label_menu.add_command(label="delete unit",
                                command=self.delete_unit)
                unit_label_menu.add_command(label="rename unit",
                                command=self.rename_unit)
                unit_label_menu.add_command(label="new unit",
                                command=self.add_unit)
                unit_label_menu.add_command(label="new test",
                                command=self.add_test_from_unit)

                if unit.tests:
                    # @TODO sort the tests better
                    for test_key in sorted(unit.tests.keys()):
                        
                        test = unit.tests[test_key]
                        
                        test_frame = ttk.Frame(unit_frame, padding="10 0 0 0")
                        test_frame.pack(fill='x')
                        
                        test_label = ttk.Label(test_frame, text=test.name)
                        test_label.pack(padx=0, anchor='w')
                                                
                        test_label_menu = tk.Menu(test_label)
                        def right_click_test(e):
                            self.clicked_widget = e.widget
                            test_label_menu.post(e.x_root, e.y_root)
                        
                        test_label.bind("<1>", self.focus_test)
                        test_label.bind("<3>", lambda e: right_click_test(e))
                        test_label_menu.add_command(label="delete test",
                                         command=self.delete_test)
                        test_label_menu.add_command(label="rename test",
                                         command=self.rename_test)
                        test_label_menu.add_command(label="new test",
                                         command=self.add_test_from_test)

                        test_type_label = ttk.Label(test_frame, text=test.type)
                        test_type_label.pack(padx=10, anchor='w')
                        
                else:
                    test_label = ttk.Label(unit_frame, text="No Tests")
                    test_label.pack(anchor='w', padx=10)
                    
                    # @TODO add right click on the no tests label back.
                    # currently it only works with one of the test_label_menus
                    # test_label_menu = tk.Menu(test_label)
                    # def right_click_test(e):
                    #     self.clicked_widget = e.widget
                    #     test_label_menu.post(e.x_root, e.y_root)
                    
                    # test_label.bind("<3>", lambda e: right_click_test(e))
                    # test_label_menu.add_command(label="new test",
                    #                     command=self.add_test_from_no_test)
        else:
            sep = ttk.Separator(frame, orient='horizontal')
            sep.pack(fill='x')
            
            unit_label = ttk.Label(frame, text="No Units")
            unit_label.pack(padx=10, anchor='w')
            
            unit_label_menu = tk.Menu(unit_label)
            def right_click_unit(e):
                self.clicked_widget = e.widget
                unit_label_menu.post(e.x_root, e.y_root)
            
            unit_label.bind("<3>", lambda e: right_click_unit(e))
            unit_label_menu.add_command(label="new unit",
                            command=self.add_unit)
        

    # returns the test or unit object in the project object tree
    # correlating to the widget that the user clicked on (should be a label)
    # defaults to self.clicked_widget
    def get_clicked_test_or_unit(self, widg=None):
        if widg == None:
            widg = self.clicked_widget
        
        # print("\n======================================")
        # print("clicked widget:", widg)
        # print("masters' children:", widg.master.children)
        # print("=======================================")
        
        # search up the widget hierarchy for the canvas widget holding the
        # selected widget, storing each preceding widget in widg_parents
        widg.widgetName
        current_widg = widg
        widg_parents = []
        while current_widg.master.widgetName != 'canvas': # type: ignore
            widg_parents.append(current_widg)
            current_widg = current_widg.master
            # print(current_widg, current_widg.widgetName, end='\n\n') # type: ignore
        
        
        # print("==============")
        # print(len(widg_parents), widg_parents)
        # depending on the depth, the widget either holds a unit or a test
        if len(widg_parents) == 2: # unit
            unit_label = widg_parents[0]
            unit_frame = widg_parents[1]
            # print(f"unit {unit_label.cget('text')}")
            # print(self.parent.project[unit_label.cget('text')])
            
            # return the unit object
            return self.parent.project[unit_label.cget('text')]
        elif len(widg_parents) == 3: # test
            test_label = widg_parents[0]
            test_frame = widg_parents[1]
            unit_frame = widg_parents[2]
            unit_label = unit_frame.children['!label']
            # print(f"test {test_label.cget('text')} in unit {unit_label.cget('text')}")
            # print(self.parent.project[unit_label.cget('text')][test_label.cget('text')])
            
            # return the test object. note the double access 
            return self.parent.project[unit_label.cget('text')][test_label.cget('text')]
        else:
            # in case of a different depth, throw an error. This should not happen
            # in normal use
            raise Exception("nesting depth issue in get_current_test_or_unit")
        
        
    
    def delete_test(self):
        test = self.get_clicked_test_or_unit()
        if messagebox.askyesno(message=
                "Are you sure you want to delete the following test:\n\n"
                + test.name, title="Delete Test"):
            test.parent.remove_test(test.name)
            self.render()
        
    
    def rename_test(self):
        test = self.get_clicked_test_or_unit()
        new_name = simpledialog.askstring(title="Rename Test", 
            prompt="Enter a new name for the following test\n" + test.name)
        if new_name in test.parent.tests:
            print("test {} already exists. renaming test {} failed".format(new_name, test.name))
        else:
            test.parent.rename_test(test.name, new_name)
            self.render()
            
    def add_test_from_test(self):
        test = self.get_clicked_test_or_unit()
        unit = test.parent
        self.add_test(unit)
            
    def add_test_from_unit(self):
        unit = self.get_clicked_test_or_unit()
        self.add_test(unit)
    
    def add_test_from_no_test(self):
        parent = self.clicked_widget.master
        unit_name = parent.children['!label'].cget('text')
        unit = self.proj[unit_name]
        self.add_test(unit)
    
    def add_test(self, unit):
        test_prompt_window = tk.Toplevel(self.parent)
        test_prompt_window.transient(self.parent)
        test_prompt_window.grab_set()
        test_prompt_window.focus_force()
        # self.parent.wait_window(test_prompt_window) # not necessary?
        
        test_prompt_window.title("New Test")
        # @TODO put window in center of parent window
        test_prompt_window.geometry("+500+500")
        test_prompt_window.resizable(False, False)
        
        name_label = ttk.Label(test_prompt_window, text="Test Name")
        name_label.grid(row=0, column=0, padx=4, pady=4)
        
        name_var = tk.StringVar(test_prompt_window)
        name_entry = ttk.Entry(test_prompt_window, textvariable=name_var)
        name_entry.grid(row=0, column=1, padx=4, pady=4)
        name_entry.focus_set()
        
        type_label = ttk.Label(test_prompt_window, text="Test Type")
        type_label.grid(row=1, column=0, padx=4, pady=4)
        
        type_var = tk.StringVar(test_prompt_window)
        type_dropdown = ttk.Combobox(test_prompt_window, textvariable=type_var)
        test_types = ("Voltage Reference", "Load Reference", "Current Interruption", "Speed Reference", "Steady State")
        type_dropdown['values'] = test_types
        type_dropdown.state(['readonly'])
        type_dropdown.grid(row=1, column=1, padx=4, pady=4)
        
        err_label = ttk.Label(test_prompt_window)
        err_label.grid(row=4, column=0, columnspan=2, padx=4, pady=4)
        err_label.grid_remove()
        
        def create_test(event=None):
            if name_var.get() == '':
                err_label.config(text="Please enter a test name")
                err_label.grid()
            elif False: # @TODO check for invalid characters, using validatecommand?
                pass
            elif name_var.get() in unit.tests:
                err_label.config(text=f"Test \"{name_var.get()}\" already exists")
                err_label.grid()
            elif type_var.get() == '':
                err_label.config(text="Select a test type")
                err_label.grid()
            else:
                err_label.grid_remove()
                
                unit.add_test(name_var.get(), type_var.get())
                test_prompt_window.destroy()
                self.render()

        done_button = ttk.Button(test_prompt_window, text="Create New Test", command=create_test)
        done_button.grid(row=3, column=0, columnspan=2, padx=4, pady=4)
        
        done_button.bind("<Return>", create_test)
        name_entry.bind("<Return>", lambda e: type_dropdown.focus())
        type_dropdown.bind("<Return>", lambda e: type_dropdown.event_generate('<Down>'))
        type_dropdown.bind("<space>", lambda e: type_dropdown.event_generate('<Down>'))
        type_dropdown.bind("<<ComboboxSelected>>", lambda e: done_button.focus())
        
        
            
    def delete_unit(self):
        unit = self.get_clicked_test_or_unit()
        if messagebox.askyesno(message=
                "Are you sure you want to delete the following unit and all of its tests:\n\n"
                + unit.name, title="Delete Unit"):
            self.proj.remove_unit(unit.name)
            self.render()
    
    def rename_unit(self): # @TODO handle a cancel in the askstring popup
        unit = self.get_clicked_test_or_unit()
        new_name = simpledialog.askstring(title="Rename Unit", 
            prompt="Enter a new name for the following unit\n" + unit.name)
        if new_name in self.proj.units:
            print("unit {} already exists. renaming unit {} failed".format(new_name, unit.name))
        else:
            self.proj.rename_unit(unit.name, new_name)
            self.render()

    def add_unit(self):
        unit_name = simpledialog.askstring(title="New Unit", 
            prompt="Enter a name for the new unit")
        if unit_name in self.proj.units:
            print("unit {} already exists. creating unit {} failed".format(unit_name, unit_name))
        else:
            self.proj.add_unit(unit_name)
            self.render()

    def focus_test(self, event):
        temp_test = self.get_clicked_test_or_unit(event.widget)
        if temp_test != self.parent.focused_test:
            self.parent.focused_test = temp_test
            self.parent.test_frame.show_focused_test()