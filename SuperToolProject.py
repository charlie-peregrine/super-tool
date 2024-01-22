# SuperToolProject.py, Charlie Jordan, 11/17/2023
# file containing all the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data

import tkinter as tk
from pslf_scripts import Voltage_Reference, Steady_State

import veusz_handler

# main class that holds information of units and tests
# contains title and filename of the project, as well as 
# a dictionary of the units it holds
class Project:
    def __init__(self, title="Untitled Project", filename=''):
        self.title = title
        self.file_name = ''
        self.units = {}
    
    # wrapper for write, intended for use by the gui
    # does not check if the file_name is valid
    def write_to_file_name(self, *args):
        with open(self.file_name, mode='w') as file:
            self.write(file)
            
    # internal write method, writes the project section to a file
    # and then delegates to each unit to write its details, effectively
    # recursing through the project tree
    def write(self, file):
        file.write("\t".join(
            ["P", self.title]
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
            self.title = line.split("\t")[1]
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
    def __init__(self, name="Untitled Test", type="None", parent=None): #, **kwargs):
        self.name = name
        self.type = type
        self.parent = parent
        self.attribute_dict = {}
        
        # default script and plot that say that this test type isn't set up yet
        self.script = lambda: print(f"No run script set up for this test of type '{self.type}'")
        self.plot = lambda: print(f"No plot script set up for this test of type '{self.type}'")
        
        # the default measured and simulated output files to be used in the 
        # plotting functions 
        self.plot_sim_file = ''
        self.plot_mes_file = ''
        
        self.header_info = []
        
        # depending on the chosen type, give the full set of default
        # attributes for that type.
        self.test_defaults()
        
        # @TODO this is not the right way to handle these
        # [print(i) for i in self.attribute_dict.values()]
        # for k,v in kwargs:
        #     self.attribute_dict[k] = v 
    
    # depending on the current test type set the default attributes of the test 
    def test_defaults(self):
        
        # clear attribute dict. used if test_defaults is being used to change type
        self.attribute_dict.clear()
        
        # only voltage ref set up as of yet
        if self.type == "Voltage Reference":
            print("voltage ref in test_defaults: ", self.name)
            attributes = [
                ("dyd_filename",    '',     'PATH',     True,   "dyd"),
                ("sav_filename",    '',     'PATH',     True,   "sav"),
                ("chf_filename",    '',     'PATH',     False,  "chf"),
                ("csv_filename",    '',     'PATH',     False,  "csv"),
                ("rep_filename",    '',     'PATH',     False,  "rep"),
                ("mes_filename",    '',     'PATH',     True,   "csv"),
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

            for a in attributes:
                self.attribute_dict[a[0]] = Attribute(*a)
                            
            # set the voltage reference runner as the script for voltage reference
            self.script = lambda: Voltage_Reference.run(self)
            
            # set plot files to grab from
            self.plot_sim_file = 'csv_filename'
            self.plot_mes_file = 'mes_filename'
            
            # set header info for this test type
            # format is (key, regular expression, long name)
            self.header_info = [
                ('time', r'.*time.*', "Time (x)"),
                ('vt',   r'(?=.*vt)(?=.*1)(?=.*gen).*',     "Voltage (y)"),
                ('pg',   r'(?=.*pg)(?=.*1)(?=.*gen).*',     "P (y)"),
                ('qg',   r'(?=.*qg)(?=.*1)(?=.*gen).*',     "Q (y)"),
                ('efd',  r'(?=.*efd)(?=.*1)(?=.*gen).*',    "EFD (y)"),
                ('ifd',  r'(?=.*ifd?)(?=.*1)(?=.*(?:gen|es)).*',    "IFD (y)"),
                
            ]
            
            # set the voltage reference plotter to use for the show graphs button
            self.plot = veusz_handler.plot_voltage_reference
            
        
        elif self.type == "Steady State":
            print("steady state in test_defaults:", self.name)
            attributes = [
                ("dyd_filename",        '',     'PATH',     True,   "dyd"),
                ("sav_filename",        '',     'PATH',     True,   "sav"),
                ("chf_filename",        '',     'PATH',     False,  "chf"),
                ("rep_filename",        '',     'PATH',     False,  "rep"),
                ("in_filename",         '',     'PATH',     True,   "csv"),
                ("out_filename",        '',     'PATH',     False,  "csv"),
                ("if_base",             0,      'NUM'),
                ("if_res",              0,      'NUM'),
                ("UseGenField",         False,  'BOOL'),
                ("Vbase",               0,      'NUM'),
                ("Zbranch",             0,      'NUM'),
                ]
            
            for a in attributes:
                self.attribute_dict[a[0]] = Attribute(*a)
            
            self.script = lambda: Steady_State.run(self)
            
            # set plot file to grab from, there is no measured file since
            # steady state does the silly 1 to 1 comparison plot
            self.plot_sim_file = 'out_filename'
            self.plot_mes_file = ''
            
            self.header_info = [
                ('mes',   r'.*If-meas \(pu\).*',     "Measured If (x)"),
                ('sim',   r'.*If-sim \(pu\).*',     "Simulated If (y)")
            ]
            
            # set the steady state plotter to use for the show graphs button
            self.plot = veusz_handler.plot_steady_state
            
    
    
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
            a, lines = Attribute.read(lines)
            if not a:
                break
            name, val = a
            
            if name not in self.attribute_dict:
                print(f"error: {name} not a valid test attribute. it will be ignored.")
            else:
                type_ = self.attribute_dict[name].type
                match type_:
                    case 'PATH':
                        convert_type = str      # type: ignore
                    case 'BOOL':
                        def convert_type(b: str):
                            if b == 'True':
                                return True
                            elif b == 'False':
                                return False
                            else:
                                raise ValueError()
                    case 'NUM':
                        convert_type = float    # type: ignore
                    case _:
                        print(type_ + " is not a valid attribute type. ignoring.")
                        continue
                
                try:
                    self.attribute_dict[name].var.set(convert_type(val))
                except ValueError:
                    print(f"Could not set attribute {name} of type " + \
                            f"{type_} to value {val} of type " + \
                            f"{type(val).__name__}. Ignoring this attribute.")
                
                
                # try: # @TODO this try does not work properly
                #     self.attribute_dict[name].var.set(val)
                # except tk.TclError:
                #     print(f"TclError: could not set attribute {name} of type " + \
                #         f"{self.attribute_dict[name].type} to value {val} of " + \
                #         f"type {type(val).__name__}. Ignoring this attribute.")
            
        
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
    def __init__(self, name, value, type_, *args, unit='NO_UNITS'):
        self.name = name
        self.type = type_
        self.unit = unit
        
        if type_ == 'PATH':
            self.var = tk.StringVar(value=value)
            self.read_only_file = args[0]
            self.extension = args[1]
        elif type_ == 'BOOL':
            self.var = tk.BooleanVar(value=value)
        else:
            self.var = tk.DoubleVar(value=value)
    
    def write(self, file):
        file.write("\t".join([
                "A", self.name, str(self.var.get())
        ]) + "\n")
    
    @staticmethod
    def read(lines):
        line = lines.pop()
        
        print('a', line)

        if line == '':
            return False, lines
        
        if line[0] == 'A':
            name, val = line.split("\t")[1:3]
            return (name, val), lines
        
        elif line[0] in 'UT':
            lines.append(line)
            return False, lines
        else:
            raise ValueError("not an attribute")
        
    
    # string conversion overload
    def __str__(self):
        return "      [A {} | {} | {} | {} ]".format(
            self.name, self.type, self.var.get(), self.unit
        )
    