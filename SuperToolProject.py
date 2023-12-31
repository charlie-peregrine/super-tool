# SuperToolProject.py, Charlie Jordan, 11/17/2023
# file containing all the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data

import tkinter as tk
from pslf_scripts import Voltage_Reference

# main class that holds information of units and tests
# contains title and filename of the project, as well as 
# a dictionary of the units it holds
class Project:
    def __init__(self, title="Untitled Project", filename=''):
        self.title = title
        self.file_name = "default-project.pec"
        self.units = {}
    
    # wrapper for write, intended for use by the gui
    def write_to_file_name(self, *args):
        with open(self.file_name, mode='w') as file:
            self.write(file)
            
    # internal write method, writes the project section to a file
    # and then delegates to each unit to write its details, effectively
    # recursing through the project tree
    def write(self, file):
        file.write("\t".join(
            ["P", self.title,
                self.file_name]
            ) + "\n")
        for unit in self.units.values():
            unit.write(file)
    
    # wrapper for read method, intended for use by the gui
    # resets the dictionary of units and starts reading from the lines
    # of the file
    def read_from_file_name(self):
        with open(self.file_name, mode='r') as file:
            lines = file.read().split('\n')[::-1]

        del self.units
        self.units = {}
        
        self.read(lines)

    # internal method for reading the project from lines of a file
    # and then passing control to units to read those
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

    # add a unit to the unit dictionary
    def add_unit(self, name):
        self.units[name] = Unit(name)

    # rename a unit and update it's location in the unit dictionary
    # @TODO add error checking above this call?
    def rename_unit(self, old, new):
        self.units[new] = self.units.pop(old)
        self.units[new].name = new

    # delete a unit and delete it's tests too
    # @TODO check to see if making a custom clearing command that works
    # down through the tree is necessary
    def remove_unit(self, name):
        del self.units[name].tests
        del self.units[name]

    # printout for the project and all of its subsections
    # overloads str(project) and print(project)
    def __str__(self):
        return "[P {} | {}]".format(self.title, self.file_name) + \
            "".join(["\n" + str(i) for i in self.units.values()])
    
    def __getitem__(self, key):
        return self.units[key]


# class containing a unit, its information, and its tests
class Unit:
    def __init__(self, name="Untitled Unit"):
        self.name = name
        self.tests = {}
        # @TODO put more unit specific info here
        
    # add a test to this unit given a name and type
    def add_test(self, name, type_):
        self.tests[name] = Test(name=name, type=type_)
        self.tests[name].parent = self
    
    # rename a test in the test dictionary and update it's location
    def rename_test(self, old, new):
        self.tests[new] = self.tests.pop(old)
        self.tests[new].name = new
        
    # remove a test from the dictionary
    def remove_test(self, name):
        del self.tests[name]
    
    # internal write method to write a unit and its tests to a file
    def write(self, file):
        file.write("\t".join(
            ["U", self.name]
            ) + "\n")
        for test in self.tests.values():
            test.write(file)
    
    # internal read method to read a unit and its tests from the lines of a file
    def read(self, lines):
        line = lines.pop()
        print('u', line)
        
        # if there are no more lines to read end the command
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
    
    # overload string conversion
    def __str__(self):
        return "  [U {}]".format(self.name) + \
            "".join(["\n" + str(i) for i in self.tests.values()]) 
    
    # allow indexing of the test dictionary
    # setitem and delitem are not included (yet)
    def __getitem__(self, key):
        return self.tests[key]
        

# test class that contains a test, its name, type, and parent unit,
# a dictionary of attributes, and a script to run based on the type
# of test that it is
class Test:
    def __init__(self, name="Untitled Test", type="None", parent=None, **kwargs):
        self.name = name
        self.type = type
        self.parent = parent
        self.attribute_dict = {}
        
        # default script says that this test type isn't set up yet
        self.script = lambda: print("No script set up for this test")
        
        # depending on the chosen type, give the full set of default
        # attributes for that type.
        self.test_defaults()
        
        # @TODO this is not the right way to handle these
        # [print(i) for i in self.attribute_dict.values()]
        for k,v in kwargs:
            self.attribute_dict[k] = v 
        
    # depending on the current test type set the default attributes of the test 
    def test_defaults(self):
        # only voltage ref set up as of yet
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
            
            # set the voltage reference runner as the script for voltage reference
            self.script = lambda: Voltage_Reference.run(self)
            
            for n,v,t in attributes:
                self.attribute_dict[n] = Attribute(n,v,t)
                # print(self.attribute_dict[n])
            # [print(i) for i in self.attribute_dict.values()]
        else:
            # script changed to print out the current type info as well
            self.script = lambda: print(f"No script set up for this test of type {self.type}")
    
    # internal write method to write a test and its attributes to a file
    def write(self, file):
        file.write("\t".join([
                "T", self.name, self.type]
                ) + "\n")
        for attr in self.attribute_dict.values():
            attr.write(file)
    
    # internal read method to read in a test and its attributes from 
    # the lines of a file
    def read(self, lines):
        line = lines.pop()
        print('t', line, )
        
        # if there are no more lines to read finish the read
        if line == '':
            return False, lines
        
        # read the line and assign the data properly
        if line[0] == "T":
            # parent is assigned when the test is added
            # to the parent unit's test list
            _, self.name, self.type = line.split("\t")
            self.test_defaults()
        elif line[0] == "U":
            lines.append(line)
            return False, lines
        else:
            raise ValueError("not a unit or test")
        
        # read in attributes
        while lines:
            a, lines = Attribute('ERR', 'ERR', 'ERR').read(lines)
            if not a:
                break
            
            self.attribute_dict[a.name] = a
        
        return self, lines
    
    # overload string conversion
    def __str__(self):
        return "    [T {} | {} | {} ]".format(
            self.name, self.type, len(self.attribute_dict.keys())
            ) + "".join(["\n" + str(i) for i in self.attribute_dict.values()])
    
    # overloading indexing operator, note that this is a get from the variable,
    # not just accessing the attribute in the dictionary
    def __getitem__(self, key):
        return self.attribute_dict[key].var.get()


# attribute class that stores details like name, type, the measuring units,
# and a tk variable that updates with the gui
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
    
    # string conversion overload
    def __str__(self):
        return "      [A {} | {} | {} | {} ]".format(
            self.name, self.type, self.var.get(), self.unit
        )
    