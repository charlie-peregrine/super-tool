# Test.py, Charlie Jordan, 1/22/2024
# class that contains tests for the supertool gui

import tkinter as tk

from supertool.pslf_scripts import Voltage_Reference, Steady_State
from supertool.pslf_scripts import Current_Interruption
import supertool.veusz_handler as veusz_handler

from supertool.SuperToolProject.Attribute import Attribute

# test class that contains a test, its name, type, and parent unit,
# a dictionary of attributes, and a script to run based on the type
# of test that it is
class Test:
    def __init__(self, name="Untitled Test", type="None", parent=None): #, **kwargs):
        self.name = name
        self.type = type
        self.parent = parent
        self.attrs = {}
        
        self.frame = None
        
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
            attributes = [
                ("dyd_filename",    '',     'PATH',     True,   "dyd",  "Dyn Data File",    "This is the dynamics data file used as input to the simulation. This contains the model names, parameters, bus numbers & voltages, etc. "),
                ("sav_filename",    '',     'PATH',     True,   "sav",  "Save Case File",   "This is the save case file used as input to the simulation. This contains the arrangement of the buses, machines, lines, etc., along with initialized values."),
                ("chf_filename",    '',     'PATH',     False,  "chf",  "Channel File",     "This is GE proprietary output file of the simulation run, which contains all the outputs of the models' output channels during the length of the simulation."),
                ("csv_filename",    '',     'PATH',     False,  "csv",  "CSV - Sim Data",   "This is output file containing the simulation data, as converted to the csv format."),
                ("rep_filename",    '',     'PATH',     False,  "rep",  "Report File",      "This is the report file generated with the simulation. Shoud there be any simulation issues, unsteady initial conditions, model instability issues, it would show here."),
                ("mes_filename",    '',     'PATH',     True,   "csv",  "CSV - Meas Data"   "This contains the Site recorded measured data presented in the csv format, used to compare against the simulated data. "),
                ("StepTimeInSecs",  0.745,  'NUM',      "sec",  "Start Step Time",      "At this time in seconds (s), the Vstep is applied to the simulation run."),
                ("UpStepInPU",      0.02,   'NUM',      "pu",   "Up Vstep size",        "At the begin time of the step, this Vstep (pu) is applied to the simulation run."),
                ("DnStepInPU",      0.02,   'NUM',      "pu",   "Down VStep size",      "At the end time of the step, this Vstep (pu) is removed from the simulation run."),
                ("StepLenInSecs",   11.99,  'NUM',      "sec",  "Step Length",          "This time in seconds (s) is the length of the step, after which the downstep will be applied."),
                ("TotTimeInSecs",   25.735, 'NUM',      "sec",  "Sim run time",         "This time in seconds (s) is the total length of the simulation run."),
                ("PSS_On",          False,  'BOOL',     "",     "PSS On?",              "If a relevant Power System Stabilizer  Model is included in the *.dyd, then unchecking this box disables the pss model in the simulation run."),
                ("SysFreqInHz",     60,     'NUM',      "Hz",   "System Freq",          "In general, The system frequency in US is 60 Hz."),
                ("SimPtsPerCycle",  8,      'NUM',      "",     "Sim Pts per Cycle",    "the simulation delta step is calculated as 1 / (System Frequency * Simulation Points Per Cycle). This number is usually 4 or 8"),
                ("set_loadflow",    True,   'BOOL',     "",     "Set Loadflow?",        "Do you want to set the loadflow for this simulation run with the below values? This does not overwrite the save case, just loads initialized values in for this simulation run."),
                ("save_loadflow",   False,  'BOOL',     "",     "Save Loadflow?",       "Do you want to save the loadflow for this simulation run with the below values? This will overwrite the values in the load flow."),
                ("Pinit",           0,      'NUM',      "MW",   "Init Gen P",           "Initialized value of Real Power of the generator model set into the *.sav loadflow."),   # MW
                ("Qinit",           0,      'NUM',      "MVAR", "Init Gen Q",           "Initialized value of Reactive Power of the generator model set into the *.sav loadflow."),   # MVAR
                ("MVAbase",         0,      'NUM',      "MVA",  "Gen MVA Rating",       "MVA base of the generator, as indicated on the nameplate."),
                ("Vinit",           0,      'NUM',      "kV",   "Init Gen Vt",          "Initialized value of terminal voltage of the generator model set into the *.sav loadflow."),   # kV,
                ("Vbase",           0,      'NUM',      "kV",   "Gen Vt Rating",        "Terminal Voltage base of the generator, as indicated on the nameplate."),   # kV,
                ("Zbranch",         0.05,   'NUM',      "pu",   "System Impedance",     "The impedane of the system, as seen by the unit, on a 100MVA base. Can use per unitized measured X=dV/dQ to approximate impedance."),   # pu
            ]

            for a in attributes:
                self.attrs[a[0]] = Attribute(*a)

            # default initialize header structures
            keys = ['time', 'vt', 'pg', 'qg', 'efd', 'ifd']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
                self.mes_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]

            # set the voltage reference runner as the script for voltage reference
            self.script = lambda no_gui: Voltage_Reference.run(self, no_gui=no_gui)
            
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
                self.attrs[a[0]] = Attribute(*a)
            
            keys = ['mes', 'sim']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
            
            self.script = lambda no_gui: Steady_State.run(self, no_gui=no_gui)
            
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
            attributes = [
                ("dyd_filename",    '',     'PATH',     True,   "dyd"),
                ("sav_filename",    '',     'PATH',     True,   "sav"),
                ("chf_filename",    '',     'PATH',     False,  "chf"),
                ("csv_filename",    '',     'PATH',     False,  "csv"),
                ("rep_filename",    '',     'PATH',     False,  "rep"),
                ("mes_filename",    '',     'PATH',     True,   "csv"),
                ("tripTimeInSecs",   2.0,    'NUM'),
                ("totTimeInSec",    36,     'NUM'),
                ("PSS_On",          False,  'BOOL'),    # 0:disable PSS model, 1: enable PSS model */
                ("change_Pref",     True,   'BOOL'),    # 1:Change Pref after breaker opens, 0: no change */
                ("offline_Pref",    0.004,  'NUM'),     # note GGOV model uses 1 as base offline while HYG3 and IEEE1 use 0 */
                ("change_Vref",     False,  'BOOL'),    # 1:Change Vref after breaker opens, 0: no change */
                ("offline_Vref",    0.79,   'NUM'),
                ("AVR_On",          False,  'BOOL'),    # 0: Exciter in Manual, 1: Exciter in Auto */
                ("set_loadflow",    False,  'BOOL'),
                ("save_loadflow",   False,  'BOOL'),
                ("Pinit",           0,      'NUM'),   # MW
                ("Qinit",           0,      'NUM'),   # MVAR
                ("MVAbase",         0,      'NUM'),
                ("Vinit",           0,      'NUM'),   # kV,
                ("Vbase",           0,      'NUM'),   # kV,
                ("Zbranch",         0,      'NUM')   # pu
            ]

            for a in attributes:
                self.attrs[a[0]] = Attribute(*a)

            # default initialize header structures
            # @TODO reset these on change?
            keys = ['time', 'vt', 'pg', 'qg', 'efd', 'ifd', 'freq']
            for k in keys:
                self.sim_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]
                self.mes_headers[k] = [tk.StringVar(), tk.StringVar(value="*1")]

            # set the voltage reference runner as the script for voltage reference
            self.script = lambda no_gui: Current_Interruption.run(self, no_gui=no_gui)
            
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
            
            # set the voltage reference plotter to use for the show graphs button
            self.plot = veusz_handler.plot_current_interruption
            
        
    
    # internal write method to write a test and its attributes to a file
    def write(self, file):
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
            
            #@TODO somewhere here check if the path attribute files exist
            
            if name not in self.attrs:
                print(f"error: {name} not a valid test attribute. it will be ignored.")
            else:
                type_ = self.attrs[name].type
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
                    self.attrs[name].var.set(convert_type(val))
                except ValueError:
                    print(f"Could not set attribute {name} of type " + \
                            f"{type_} to value {val} of type " + \
                            f"{type(val).__name__}. Ignoring this attribute.")
                
                
                # try: # @TODO this try does not work properly
                #     self.attrs[name].var.set(val)
                # except tk.TclError:
                #     print(f"TclError: could not set attribute {name} of type " + \
                #         f"{self.attrs[name].type} to value {val} of " + \
                #         f"type {type(val).__name__}. Ignoring this attribute.")
            
        
        return self, lines
    
    def add_attr(self, name, val):
        if name in self.attrs:
            type_ = self.attrs[name].type
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
                    return
            
            try:
                self.attrs[name].var.set(convert_type(val))
            except ValueError:
                print(f"Could not set attribute {name} of type " + \
                        f"{type_} to value {val} of type " + \
                        f"{type(val).__name__}. Ignoring this attribute.")
        else:
            print(f"error: {name} not a valid test attribute. it will be ignored.")
    
    # overload string conversion
    def __str__(self):
        return "    [T {} | {} | {} ]".format(
            self.name, self.type, len(self.attrs.keys())
            ) + "".join(["\n" + str(i) for i in self.attrs.values()])
    
    # overloading indexing operator, note that this is a get from the variable,
    # not just accessing the attribute in the dictionary
    def __getitem__(self, key):
        return self.attrs[key].var.get()
