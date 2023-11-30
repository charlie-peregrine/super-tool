# ProjectView.py, Charlie Jordan, 11/28/2023
# Contains the frame for the project panel and
# all of its derivatives


import tkinter as tk
from tkinter import ttk
from SuperToolFrames import ScrollFrame

from functools import partial

class ProjectView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                    height=300, width=300)
        self.grid(row=0,column=0, columnspan=1, rowspan=2, sticky="nesw")

        self.proj = parent.project
        
        # @TODO font size up of header
        self.proj_header = ttk.Label(self, text=self.proj.title)
        self.proj_header.grid(row=0, column=0, columnspan=3, sticky='w')
        
        self.scroller = ScrollFrame(self)
        self.scroller.grid(row=1, column=0, sticky='nesw')
        
        # a = stp.Unit()
        # b = stp.Unit()
        # a.test_dict = {-1 : stp.Test(), 1 : stp.Test()}
        # b.test_dict = {3 : stp.Test(), 2 : stp.Test(), 4 : stp.Test()}
        # b.name = "Unit AAAAAAAAAAAAAAAAAAA"
        # proj.unit_list = [a] #,b, stp.Unit(), b, a, a]
        
        self.proj.add_unit("Example Unit!!!")
        self.proj["Example Unit!!!"].add_test("test one", "load ref")
        self.proj["Example Unit!!!"].add_test("test two", "load ref")
        self.proj["Example Unit!!!"].add_test("test three", "load ref")
        self.proj["Example Unit!!!"].add_test("test four", "load ref")
        self.proj["Example Unit!!!"].add_test("test five", "load ref")
        # self.proj["Example Unit!!!"].add_test("second test", "dynamic")
        self.proj.add_unit("Second Unit")
        self.proj.add_unit("3 U")
        self.proj.add_unit("AAAAAAAAAAAAA")
        u = self.proj["Second Unit"]
        u.add_test("Idaho test 3", "load ref")
        u.add_test("4000", "Evil Test Type >:)")
        
        self.dummy_label = ttk.Label(self)
        
        self.render()
        
    def render(self):
        
        frame = self.scroller.frame
        # clear the scroller frame if there's anything in it
        for widget in frame.winfo_children():
            widget.destroy()
        
        self.clicked_widget = self.dummy_label
        
        self.units = {}
        self.tests = {}
        if self.proj.units:
            for unit_key in sorted(self.proj.units.keys()):
                
                unit = self.proj.units[unit_key]
                sep = ttk.Separator(frame, orient='horizontal')
                sep.pack(fill='x')
                
                unit_frame = ttk.Frame(frame, padding='10 0 0 4')
                unit_frame.pack(fill='x')
                
                unit_label = UnitLabel(unit_frame, text=unit.name)
                unit_label.pack(anchor='w')
                self.units[unit.name] = unit

                unit_label_menu = tk.Menu(unit_label)
                def right_click_unit(e):
                    self.clicked_widget = e.widget
                    unit_label_menu.post(e.x_root, e.y_root)
                
                unit_label.bind("<3>", lambda e: right_click_unit(e))
                unit_label_menu.add_command(label="delete unit",
                                command=self.delete_unit)
                unit_label_menu.add_command(label="rename unit",
                                command=self.rename_unit)

                if unit.tests:
                    # @TODO sort the tests better
                    for test_key in sorted(unit.tests.keys()):
                        
                        test = unit.tests[test_key]
                        
                        test_frame = ttk.Frame(unit_frame, padding="10 0 0 0")
                        test_frame.pack(fill='x')
                        
                        test_label = TestLabel(test_frame, text=test.name)
                        test_label.pack(padx=0, anchor='w')
                        self.tests[test.name] = (unit, test)
                        
                        test_label_menu = tk.Menu(test_label)
                        def right_click_test(e):
                            self.clicked_widget = e.widget
                            test_label_menu.post(e.x_root, e.y_root)
                        
                        test_label.bind("<3>", lambda e: right_click_test(e))
                        test_label_menu.add_command(label="delete test",
                                         command=self.delete_test)
                        test_label_menu.add_command(label="rename test",
                                         command=self.rename_test)
                        # menu.add_command(label="rename",
                        #                  command=lambda : self.rename_test(test_number))

                        test_type_label = ttk.Label(test_frame, text=test.type)
                        test_type_label.pack(padx=10, anchor='w')
                        
                else:
                    test_label = ttk.Label(unit_frame, text="No Tests")
                    test_label.pack(anchor='w', padx=10)
        else:
            sep = ttk.Separator(frame, orient='horizontal')
            sep.pack(fill='x')
            
            unit_label = ttk.Label(frame, text="No Units")
            unit_label.pack(padx=10, anchor='w')
        
        
        
    def delete_test(self):
        parent, test = self.tests[self.clicked_widget.cget("text")]
        parent.remove_test(test.name)
        self.render()
    
    def rename_test(self):
        parent, test = self.tests[self.clicked_widget.cget("text")]
        # popup
        # get info
        new_name = "frog!"
        if new_name in parent.tests.keys():
            print("test {} already exists. renaming test {} failed".format(new_name, test.name))
        else:
            parent.rename_test(test.name, new_name)
            self.render()
    
    def delete_unit(self):
        unit = self.units[self.clicked_widget.cget("text")]
        self.proj.remove_unit(unit.name)
        self.render()
    
    def rename_unit(self):
        unit = self.units[self.clicked_widget.cget("text")]
        # popup
        # get info
        new_name = "bog!"
        if new_name in self.proj.units.keys():
            print("unit {} already exists. renaming unit {} failed".format(new_name, unit.name))
        else:
            self.proj.rename_unit(unit.name, new_name)
            self.render()

class UnitTriad():
    pass

class UnitLabel(ttk.Label):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(self.parent, **kwargs)
        
        self.menu = ProjectUnitMenu(self)
        self.bind('<3>', lambda e: self.menu.post(e.x_root, e.y_root))

class TestLabel(ttk.Label):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(self.parent, **kwargs)
        
        self.menu = ProjectTestMenu(self)
        self.bind('<3>', lambda e: self.menu.post(e.x_root, e.y_root))
    
    def delete(self):
        project_view = self.parent.parent.parent
        project_view.proj


class ProjectUnitMenu(tk.Menu):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(self.parent)
        
        self.add_command(label="Rename Unit")
        self.add_command(label="Delete Unit")
        self.add_command(label="Add Test")

class ProjectTestMenu(tk.Menu):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(self.parent)
        
        self.add_command(label="Rename Test")
        self.add_command(label="Delete Test", command=parent.delete)