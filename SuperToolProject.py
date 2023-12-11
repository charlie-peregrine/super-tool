# SuperToolProject.py, Charlie Jordan, 11/17/2023
# file containing all the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data

import tkinter as tk
from collections import deque

class Project:
    def __init__(self, filename=''):
        self.title = "Untitled Project"
        self.file_name = "default-project.pec"
        self.units = {}
    
    def write_to_file_name(self, *args):
        with open(self.file_name, mode='w') as file:
            self.write(file)
            
    def write(self, file):
        file.write("\t".join(
            ["P", self.title,
                self.file_name]
            ) + "\n")
        for unit in self.units.values():
            unit.write(file)
    
    def read_from_file_name(self):
        with open(self.file_name, mode='r') as file:
            lines = file.read().split('\n')[::-1]

        del self.units
        self.units = {}
        
        self.read(lines)

    def read(self, lines):
        line = lines.pop()
        print('p', line)
        if line[0] == "P":
            _, self.title, self.file_name = line.split("\t")
        else:
            raise ValueError("not a project")
        print(self)
        
        while lines:
            u, lines = Unit().read(lines)
            if not u:
                break
            self.units[u.name] = u

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
        return "[P {} | {}]".format(self.title, self.file_name) + \
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
        
    def write(self, file):
        file.write("\t".join(
            ["U", self.name]
            ) + "\n")
        for test in self.tests.values():
            test.write(file)
    
    def read(self, lines):
        line = lines.pop()
        print('u', line)
        
        if line == '':
            return False, lines
        
        if line[0] == "U":
            _, self.name = line.split("\t")
        else:
            raise ValueError("not a unit")
        
        while lines:
            t, lines = Test().read(lines)
            if not t:
                break
            t.parent = self
            self.tests[t.name] = t
        
        return self, lines
            
    def __str__(self):
        return "  [U {}]".format(self.name) + \
            "".join(["\n" + str(i) for i in self.tests.values()]) 
    
    def __getitem__(self, key):
        return self.tests[key]
        
class Test:
    # @TODO handle kwargs
    def __init__(self, name="Untitled Test", type="None", parent=None, **kwargs):
        self.name = name
        self.type = type
        self.parent = parent
        self.attribute_dict = {}
        
        
        # depending on the chosen type, give the full set of default
        # attributes for that type.
        self.default_attributes()
        
        
        
        [print(i) for i in self.attribute_dict.values()]
        for k,v in kwargs:
            self.attribute_dict[k] = v 
        
    def default_attributes(self):
        if self.type == "Voltage Reference":
            print("wahoo", self.name)
            attributes = [
                ("dyd_filename", '', 'PATH'),
                ("sav_filename", '', 'PATH'),
                ("chf_filename", '', 'PATH'),
                ("csv_filename", '', 'PATH'),
                ("rep_filename", '', 'PATH'),
                ("StepTimeInSecs",  0,       'NUM'),
                ("UpStepInPU",      0,       'NUM'),
                ("DnStepInPU",      0,       'NUM'),
                ("StepLenInSecs",   0,       'NUM'),
                ("TotTimeInSecs",   0,      'NUM'),
                ("PSS_On",          False,  'BOOL'),
                ("SysFreqInHz",     0,      'NUM'),
                ("SimPtsPerCycle",  0,      'NUM'),
                ("set_loadflow",    False,  'BOOL'),
                ("save_loadflow",   False,  'BOOL'),
                ("Pinit",           0,      'NUM'),   # MW
                ("Qinit",           0,      'NUM'),   # MVAR
                ("MVAbase",         0,      'NUM'),
                ("Vinit",           0,      'NUM'),   # kV,
                ("Vbase",           0,      'NUM'),   # kV,
                ("Zbranch",         0,      'NUM'),   # pu
            ]
            for n,v,t in attributes:
                self.attribute_dict[n] = Attribute(n,v,t)
                # print(self.attribute_dict[n])
            [print(i) for i in self.attribute_dict.values()]
        else:
            # self.attribute_dict["dummy"] = Attribute("dummy", 0, '', 'sec')
            pass
    
    
    def write(self, file):
        file.write("\t".join([
                "T", self.name, self.type]
                ) + "\n")
        for attr in self.attribute_dict.values():
            attr.write(file)
    
    def read(self, lines):
        line = lines.pop()
        print('t', line, )
        
        if line == '':
            return False, lines
        
        if line[0] == "T":
            _, self.name, self.type = line.split("\t")
            # parent is assigned when the test is added to the parent unit's test list
            
            self.default_attributes()
        elif line[0] == "U":
            lines.append(line)
            return False, lines
        else:
            raise ValueError("not a unit")
        
        while lines:
            a, lines = Attribute('ERR', 'ERR', 'ERR').read(lines)
            if not a:
                break
            
            self.attribute_dict[a.name] = a
        
        return self, lines
    
    def __str__(self):
        return "    [T {} | {} | {} ]".format(
            self.name, self.type, len(self.attribute_dict.keys())
            ) + "".join(["\n" + str(i) for i in self.attribute_dict.values()])

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
    
    def write(self, file):
        file.write("\t".join([
                "A", self.name, str(self.var.get()), self.type, self.unit
        ]) + "\n")
    
    def read(self, lines):
        line = lines.pop()
        
        print('a', line)

        if line == '':
            return False, lines
        
        if line[0] == 'A':
            _, self.name, val, self.type, self.unit = line.split("\t")
            if self.type == 'PATH':
                self.var = tk.StringVar(value=val)
            elif self.type == 'BOOL':
                self.var = tk.BooleanVar(value=val)
            else:
                self.var = tk.DoubleVar(value=val)
        elif line[0] in 'UT':
            lines.append(line)
            return False, lines
        else:
            raise ValueError("not an attribute")
        
        return self, lines
    
    def __str__(self):
        return "      [A {} | {} | {} | {} ]".format(
            self.name, self.type, self.var.get(), self.unit
        )