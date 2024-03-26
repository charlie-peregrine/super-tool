# Test.py, Charlie Jordan, 1/22/2024
# class that contains tests for the supertool gui

import tkinter as tk

from supertool.pslf_scripts import Voltage_Reference, Steady_State, Speed_Reference
from supertool.pslf_scripts import Current_Interruption, Load_Reference, Synchronization
import supertool.veusz_handler as veusz_handler
import supertool.consts as consts

from supertool.SuperToolProject.Attribute import Attribute

# test class that contains a test, its name, type, and parent unit,
# a dictionary of attributes, and a script to run based on the type
# of test that it is
class Test:
    def __init__(self, name="Untitled Test", type_="None", parent=None): #, **kwargs):
        self.name = name
        self.type = type_
        self.parent = parent
        self.attrs: dict[str,Attribute] = {}
        
        self.sub_dir = ''
        
        self.frame = None
        self.hovertext = None
        
        # default script and plot that say that this test type isn't set up yet
        self.script = lambda: print(f"No run script set up for this test of type '{self.type}'")
        self.plot = lambda: print(f"No plot script set up for this test of type '{self.type}'")
        
        # the default measured and simulated output files to be used in the 
        # plotting functions 
        self.plot_sim_file = ''
        self.plot_mes_file = ''
        
        self.header_info = []
        
        self.sim_headers = {}
        self.mes_headers = {}
        
        # depending on the chosen type, give the full set of default
        # attributes for that type.
        self.test_defaults()
        
        # @TODO this is not the right way to handle these
        # [print(i) for i in self.attrs.values()]
        # for k,v in kwargs:
        #     self.attrs[k] = v 
    
    # depending on the current test type set the default attributes of the test 
    def test_defaults(self):
        
        # clear attribute dict. used if test_defaults is being used to change type
        self.attrs.clear()
        
        # clear simulated and measured files so changing from a done test type 
        # to a wip test type doesn't throw a keyerror
        self.plot_sim_file = ''
        self.plot_mes_file = ''
        
        self.x_range_min = tk.StringVar()
        self.x_range_max = tk.StringVar()
        
        # only voltage ref set up as of yet
        if self.type == "Voltage Reference":
            print("voltage ref in test_defaults: ", self.name)

            # print(consts.DEFAULT_TEST_ATTRIBUTES['vstep'])
            for n, d in consts.DEFAULT_TEST_ATTRIBUTES['vstep'].items():
                # print(n, str(d)[:50])
                self.attrs[n] = Attribute(self, n, d)

            # set the voltage reference runner as the script for voltage reference
            self.script = lambda no_gui: Voltage_Reference.run(self, no_gui=no_gui)

            # default initialize header structures
            keys = ['time', 'vt', 'pg', 'qg', 'efd', 'ifd']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
                self.mes_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
            
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
                ('ifd',  r'(?=.*ifd?)(?=.*1)(?=.*(?:gen|es)).*',    "IFD (y)")
            ]
            
            # set the voltage reference plotter to use for the show graphs button
            self.plot = veusz_handler.plot_voltage_reference
            
        
        elif self.type == "Steady State":
            print("steady state in test_defaults:", self.name)
            
            # print(consts.DEFAULT_TEST_ATTRIBUTES['steadystate'])
            for n, d in consts.DEFAULT_TEST_ATTRIBUTES['steadystate'].items():
                # print(n, str(d)[:50])
                self.attrs[n] = Attribute(self, n, d)
            
            # set the steady state runner as the script for steady state
            self.script = lambda no_gui: Steady_State.run(self, no_gui=no_gui)
            
            keys = ['mes', 'sim']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
            
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
            
        elif self.type == "Current Interruption":
            print("current interrupt in test_defaults: ", self.name)

            # print(consts.DEFAULT_TEST_ATTRIBUTES['currint'])
            for n, d in consts.DEFAULT_TEST_ATTRIBUTES['currint'].items():
                # print(n, str(d)[:50])
                self.attrs[n] = Attribute(self, n, d)
            
            # set the current interruption runner as the script for current interruption
            self.script = lambda no_gui: Current_Interruption.run(self, no_gui=no_gui)

            # default initialize header structures
            # @TODO reset these on change?
            keys = ['time', 'vt', 'pg', 'qg', 'efd', 'ifd', 'freq']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
                self.mes_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
            
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
                ('freq', r'(?=.*spd)(?=.*1)(?=.*gen).*',    "Frequency (y)")
            ]
            
            # set the current interruption plotter to use for the show graphs button
            self.plot = veusz_handler.plot_current_interruption
        
        elif self.type == "Load Reference":
            print("load reference in test_defaults:", self.name)

            # print(consts.DEFAULT_TEST_ATTRIBUTES['loadref'])
            for n, d in consts.DEFAULT_TEST_ATTRIBUTES['loadref'].items():
                # print(n, str(d)[:50])
                self.attrs[n] = Attribute(self, n, d)
            
            # set the load reference runner as the script for load reference
            self.script = lambda no_gui: Load_Reference.run(self, no_gui=no_gui)

            # default initialize header structures
            # @TODO reset these on change?
            keys = ['time', 'pg', 'gate', 'head']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
                self.mes_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
            
            # set plot files to grab from
            self.plot_sim_file = 'csv_filename'
            self.plot_mes_file = 'mes_filename'
            
            # set header info for this test type
            # format is (key, regular expression, long name)
            self.header_info = [
                ('time', r'.*time.*', "Time (x)"),
                ('pg',   r'(?=.*pg)(?=.*1)(?=.*gen).*',     "P (y)"),
                ('gate', r'(?=.*gv)(?=.*1)(?=.*gen).*',     "Gate % (y)"),
                ('head',  r'(?=.*head)(?=.*1)(?=.*gen).*',    "Head (y)"),
            ]
            
            # # set the load reference plotter to use for the show graphs button
            self.plot = veusz_handler.plot_load_reference
        
        elif self.type == "Speed Reference":
            print("speed reference in test_defaults:", self.name)

            # print(consts.DEFAULT_TEST_ATTRIBUTES['speedref'])
            for n, d in consts.DEFAULT_TEST_ATTRIBUTES['speedref'].items():
                # print(n, str(d)[:50])
                self.attrs[n] = Attribute(self, n, d)
            
            # set the speed reference runner as the script for speed reference
            self.script = lambda no_gui: Speed_Reference.run(self, no_gui=no_gui)

            # default initialize header structures
            # @TODO reset these on change?
            # valve -> valve position percent, freq -> perceived frequency percent
            keys = ['time', 'pg', 'valve', 'freq']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
                self.mes_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
            
            # set plot files to grab from
            self.plot_sim_file = 'csv_filename'
            self.plot_mes_file = 'mes_filename'
            
            # set header info for this test type
            # format is (key, regular expression, long name)
            self.header_info = [
                ('time', r'.*time.*', "Time (x)"),
                ('pg',   r'(?=.*pg)(?=.*1)(?=.*gen).*',     "P (y)"),
                ('valve', r'(?=.*fsr)(?=.*1)(?=.*gov).*',    "Valve Pos % (y)"),
                ('freq', r'(?=.*tnh)(?=.*1)(?=.*gov).*',    "Perceived Freq % (y)")
            ]
            
            # # set the speed reference plotter to use for the show graphs button
            self.plot = veusz_handler.plot_speed_reference
        
        elif self.type == "Synchronization":
            print("sync mod in test_defaults:", self.name)

            # print(consts.DEFAULT_TEST_ATTRIBUTES['speedref'])
            for n, d in consts.DEFAULT_TEST_ATTRIBUTES['syncmod'].items():
                # print(n, str(d)[:50])
                self.attrs[n] = Attribute(self, n, d)
            
            # set the sync mod runner as the script for speed reference
            self.script = lambda no_gui: Synchronization.run(self, no_gui=no_gui)

            # default initialize header structures
            # @TODO reset these on change?
            keys = ['time', 'vt', 'pg', 'qg', 'efe', 'ife', 'freq']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
                self.mes_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
            
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
                ('efe',  r'(?=.*efd)(?=.*1)(?=.*gen).*',    "EFE (y)"),
                ('ife',  r'(?=.*ifd?)(?=.*1)(?=.*(?:gen|es)).*',    "IFE (y)"),
                ('freq', r'(?=.*spd)(?=.*1)(?=.*gen).*',    "Frequency (y)")
            ]
            # # set the speed reference plotter to use for the show graphs button
            self.plot = veusz_handler.plot_synchronization
            
        
    def add_attr(self, name, val):
        def str2bool(b: str):
            if b == 'True':
                return True
            elif b == 'False':
                return False
            else:
                raise ValueError()
        
        def set_val(attr, conversion, value):
            try:
                attr.var.set(conversion(value))
            except ValueError:
                print(f"Could not set attribute {attr.name} of type " + \
                        f"{attr.type} to value {value} of type " + \
                        f"{type(value).__name__}. Ignoring this attribute.")
        
        if name in self.attrs:
            attr = self.attrs[name]
            match attr.type:
                case 'PATH':
                    set_val(attr, str, val)
                case 'BOOL':
                    set_val(attr, str2bool, val)
                case 'NUM':
                    set_val(attr, float, val)
                case 'STR':
                    set_val(attr, str, val)
                case _:
                    print(attr.type + " is not a valid attribute type. ignoring.")
                    return
            
        else:
            print(f"error: {name} not a valid test attribute. it will be ignored.")
            
            # try: # @TODO this try does not work properly
            #     self.attrs[name].var.set(val)
            # except tk.TclError:
            #     print(f"TclError: could not set attribute {name} of type " + \
            #         f"{self.attrs[name].type} to value {val} of " + \
            #         f"type {type(val).__name__}. Ignoring this attribute.")
    
    def get_dir(self):
        if self.sub_dir:
            end = self.sub_dir + '/'
        else:
            end = ''
        return self.parent.get_dir() + end
    
    # overload string conversion
    def __str__(self):
        return "    [T {} | {} | {} ]".format(
            self.name, self.type, len(self.attrs.keys())
            ) + "".join(["\n" + str(i) for i in self.attrs.values()])
    
    # overloading indexing operator, note that this is a get from the variable,
    # not just accessing the attribute in the dictionary
    def __getitem__(self, key):
        return self.attrs[key].var.get()

    # DEPRECATED
    # internal write method to write a test and its attributes to a file
    def write(self, file):
        """Deprecated project save method. Use write_to_file_name instead."""
        file.write("\t".join([
                "T", self.name, self.type]
                ) + "\n")
        for attr in self.attrs.values():
            attr.write(file)
        # for k, [h, m] in self.sim_headers.items():
        #     file.write("\t".join([
        #         "1", k, h.get(), m.get()
        #     ]) + "\n")
        #     # print(k, h.get(), m.get(), sep='\t')
        # for k, [h, m] in self.mes_headers.items():
        #     file.write("\t".join([
        #         "2", k, h.get(), m.get()
        #     ]) + "\n")
            # print(k, h.get(), m.get(), sep='\t')
    
    # DEPRECATED
    # internal read method to read in a test and its attributes from 
    # the lines of a file
    def read(self, lines):
        """Deprecated project save method. Use read_from_file_name instead."""
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
            
            #@TODO somewhere here check if the path attribute files exist
            
            self.add_attr(name, val)            
        
        return self, lines
    