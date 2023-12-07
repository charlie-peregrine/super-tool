# SuperToolProject.py, Charlie Jordan, 11/17/2023
# file containing all the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data

import tkinter as tk

class Project:
    def __init__(self, filename=''):
        self.title = "Untitled Project"
        self.file_name = "default-project.pec"
        self.units = {}
    
    def write_to_file(self, *args):
        with open(self.file_name, mode='w') as file:
            file.write("\t".join(
                ["P", self.title,
                 self.file_name]
                ) + "\n")
            
            for unit in self.units.values():
                file.write("\t".join(
                    ["U", unit.name]
                    ) + "\n")
                for test in unit.tests.values():
                    file.write("\t".join([
                        "T", test.name, test.type]
                        ) + "\n")
                    # for k,v in test.attribute_dict:
                    #     write(k + "\t" + v)
            
    
    def read_from_file(self):
        pass

    def add_unit(self, name):
        self.units[name] = Unit(name)

    # @TODO add error checking above this call?
    def rename_unit(self, old, new):
        self.units[new] = self.units.pop(old)
        self.units[new].name = new

    def remove_unit(self, name):
        del self.units[name].tests
        del self.units[name]

    def __str__(self):
        return "[{} | {}]".format(self.title, self.file_name) + \
            "".join(["\n" + str(i) for i in self.units.values()])
    
    def __getitem__(self, key):
        return self.units[key]
    

class Unit:
    def __init__(self, name="Untitled Unit"):
        self.name = name
        self.tests = {}
        
    def add_test(self, name, type_):
        self.tests[name] = Test(name=name, type=type_)
        self.tests[name].parent = self
    
    def rename_test(self, old, new):
        self.tests[new] = self.tests.pop(old)
        self.tests[new].name = new
        
    def remove_test(self, name):
        del self.tests[name]
    
    def __str__(self):
        return "  [{}]".format(self.name) + \
            "".join(["\n" + str(i) for i in self.tests.values()]) 
    
    def __getitem__(self, key):
        return self.tests[key]
        
class Test:
    # @TODO handle kwargs
    def __init__(self, name="Untitled Test", type="None", parent=None, **kwargs):
        self.name = name
        self.type = type
        self.parent = parent
        self.attribute_dict = kwargs
        
    
    def __str__(self):
        return "    [ {} | {} | {} ]".format(self.name, self.type, self.attribute_dict)

class Attribute:
    def __init__(self, name, value, type_, unit='NO_UNITS'):
        self.name = name
        self.type = type_
        self.unit = unit
        if type_ == 'PATH':
            self.var = tk.StringVar(value=value)
        elif type_ == 'BOOL':
            self.var = tk.BooleanVar(value=value)
        else:
            self.var = tk.DoubleVar(value=value)
    
    def __str__(self):
        return "[ name:{}\ttype:{}\tvar:{}\tunit:{} ]".format(
            self.name, self.type, self.var, self.unit
        )