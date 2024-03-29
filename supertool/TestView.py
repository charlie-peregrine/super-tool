# TestView.py, Charlie Jordan, 12/5/2023
# file to store the gui work for the test pane of the UI

import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font
from tkinter.filedialog import askopenfilename, asksaveasfilename
import traceback
from idlelib.tooltip import Hovertip

from os.path import basename
import os
import psutil
import win32gui

from textwrap import wrap as wraptext
import supertool.consts as consts
from supertool.SuperToolFrames import ScrollFrame
from supertool.pslf_scripts.Super_Tool import SuperToolFatalError
from supertool.pslf_scripts.Super_Tool import ScriptQueue, SuperToolMessage

# Frame subclass for presenting and receving info regarding
# individual tests and their attributes
class TestView(ttk.Frame):
    def __init__(self, parent):
        # set up the frame and place it in the window
        super().__init__(parent, borderwidth=5, relief='groove',
                            height=100, width=100)
        self.parent = parent.master
        
        ### Test Parameters Box details
        # header
        test_header = ttk.Label(self, text="Test Parameters:") # @TODO font size up 
        test_header.grid(row=0, column=0, columnspan=1, sticky="w")

        # run simulation button
        self.img = tk.PhotoImage(file="./icons/supertoolplay.png")
        self.run_button = ttk.Button(self, image=self.img, command=self.run_simulation)
        self.run_button.grid(row=0, column=2, sticky='ne')

        self.run_button.bind("<3>", lambda e:
            self.parent.run_menu.post(e.x_root, e.y_root))
        self.run_button_hover = Hovertip(self.run_button, hover_delay=consts.HOVER_DELAY,
            text="Right click to open Run Menu")
        

        # Put a scroll frame in the frame
        self.scroller = ScrollFrame(self)
        self.frame = self.scroller.frame
        self.scroller.grid(row=1, column=0, columnspan=3, sticky='nesw')

        # make the applicable rows and columns resizable
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.trace_data = []
        
        self.run_sim_active = False
        self.running_thread = threading.Thread()
        
        # show the focused test. note that when it's used in the initializer,
        # the "no test selected" text will always be shown since no test
        # is selected yet
        self.show_focused_test()
        

    # helper function to show the currently focused test in the test frame
    def show_focused_test(self):
        # empty the scroller's frame, deleting that frame is a bad idea
        # because of the specific configurations set in the ScrollFrame class
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # clear variable tracebacks for deleted buttons
        for var, callback in self.trace_data:
            var.trace_remove('write', callback)
        self.trace_data.clear()

        # reset the scroller to the top of the frame
        # fixes a bug where when a large frame gets reset to a very small frame
        # the scrollbar would still act like the frame was large
        self.scroller.scroll_to_top()
        
        focused = self.parent.focused_test
        if focused: # if there is a focused test
            # put labels and buttons for the top of the scrollable frame
            self.title_label = ttk.Label(self.frame, text=focused.name)
            self.title_label.grid(row=0, column=0, sticky='w')
            self.type_label = ttk.Label(self.frame, text=focused.type)
            self.type_label.grid(row=1, column=0)
            
            # @TODO give the change type button an action
            self.type_button = ttk.Button(self.frame, text="change",
                                          command=self.change_focused_test_type)
            self.type_button.grid(row=1, column=1, sticky='e')
            
            attr_groups = {k: [] for k in ['INFILE', 'OUTFILE', 'PLAIN', 'LOADFLOW', 'USER']}
            attr_full_names = {'INFILE': "Input Files",
                               'OUTFILE': "Output Files",
                               'PLAIN': "Simulation Specific Variables",
                               'LOADFLOW': "Loadflow Variables",
                               'USER': "User Defined Variables"}
            
            for attr in focused.attrs.values():
                if attr.group and attr.group in attr_groups:
                    attr_groups[attr.group].append(attr)
                    # print(attr.group, attr_groups[attr.group])
                else:
                    print(f"Uh oh no group for {attr}")
                    continue
            
            # set up for loop, offset is how many rows down the big
            # list of attributes should start
            offset = 2
            
            # storage for all of the interactibles so they still
            # work outside of the loop
            self.interactibles = []
            
            line = offset
            for group, attr_ls in attr_groups.items():
                header = AttributeHeader(self.frame, attr_full_names[group])
                header.grid(row=line, column=0, columnspan=4, sticky='nesw', pady=1)
                line += 1
                for attr in attr_ls:
                    self.build_attr_line(attr, self.frame, line)
                    line += 1
                
            # for every attribute of the attribute dictionary, add
            # a line containing its name and relevant input fields
            # for i, attr in enumerate(focused.attrs.values()):
            #     self.build_attr_line(attr, self.frame, i+offset)
                
        else:
            # if there's no focused test, show that no test is selected
            # @TODO probably a memory leak due to dropping the old no_test_label
            self.no_test_label = ttk.Label(self.frame, text="No Test Selected. Create or click one to begin.")
            self.no_test_label.grid(row=1,column=0)
        
        self.parent.update_pane_widths()
    
    def build_attr_line(self, attr, frame, line):
        # configure values that are the same accross all types
        padding_info = {'pady': 1, 'padx': 2}
        
        # show the title label
        title_label = ttk.Label(frame, text=attr.name)
        title_label.grid(row=line, column=0, sticky='w')
        
        title_label_hover = Hovertip(title_label, text='',
                                        hover_delay=consts.HOVER_DELAY)
        
        # update title label if there's a valid long name for it
        if attr.full_name:
            title_label.config(text=attr.full_name)
            title_label_hover.text = f"{attr.full_name} ({attr.name})\n"
        else:
            title_label_hover.text = attr.name + "\n"
        
        if attr.description:
            title_label_hover.text += "\n".join(wraptext(attr.description, 45))
        else:
            title_label_hover.text += "No Attribute Description"
        
        # paths are shown with their name, their short name,
        # and a button to open a file picker window. hovering
        # over the short name shows a tooltip of the full path name
        if attr.type == 'PATH':
            # show short name of path
            def short_name(s):
                s2 = basename(s)
                ln = len(s2)
                max_len = 30
                if ln > max_len:
                    return s2[:max_len//2] + "..." \
                            + s2[-(max_len//2 - 2):]
                else:
                    return s2
            
            path_button = ttk.Button(frame, text=short_name(attr.var.get()),
                    command=lambda attr=attr: self.get_new_path(attr))
            path_button.grid(row=line, column=1, sticky='nesw', cnf=padding_info)
            
            def clear_path(e=None, attr=attr):
                attr.var.set("")
            path_button.bind("<3>", clear_path)
            
            # create hovertext for paths to show the long path instead of just the basename
            def path_hover_text(attribute):
                if attribute.var.get() == '':
                    return "Click to Select a file"
                else:
                    # print(attribute.get())
                    # print("RO:", attribute.read_only_file, end=' - ')
                    if attribute.read_only_file:
                        # check that the file itself exists
                        # print(attribute.get())
                        # print(os.path.exists(attribute.get()))
                        if not os.path.exists(attribute.get()):
                            return f"This file does not exist at this location.\n" + \
                                    f"Full Path: {attribute.get()}\n" + \
                                    f"Relative Path: {attribute.var.get()}\n" + \
                                    "Right click to clear or click to re-select a file" 
                    else:
                        # check that the parent directory exists
                        # print(attribute.parent.get_dir())
                        # print(os.path.exists(os.path.dirname(attribute.get())))
                        if not os.path.exists(os.path.dirname(attribute.get())):
                            return  "This file cannot be generated at this location.\n" + \
                                    "This is likely an issue with the working, unit,\n" + \
                                    "or test sub-directories being malformed.\n" + \
                                    f"Full Path: {attribute.get()}\n" + \
                                    f"Relative Path: {attribute.var.get()}\n" + \
                                    "Right click to clear or click to re-select a file" 
                return f"Full Path: {attribute.get()}\n" + \
                        f"Relative Path: {attribute.var.get()}\n" + \
                        "Right click to clear"
            path_label_hover = Hovertip(path_button, path_hover_text(attr), hover_delay=consts.HOVER_DELAY)
            
            # set up traces for when the path variables update to modify the path label
            # separate functions needed for clarity
            def update_button(_1=None, _2=None, _3=None, l=path_button, a=attr):
                l.configure(text=short_name(a.var.get()))
                if a.var.get():
                    if a.read_only_file:
                        if not os.path.exists(a.get()):
                            l.configure(style="badpath.TButton")
                            return
                    else:
                        if not os.path.exists(os.path.dirname(a.get())):
                            l.configure(style="badpath.TButton")
                            return
                l.configure(style="TButton")

            update_button()
            button_cb = attr.var.trace_add('write', update_button)
            
            def update_hover(_1=None, _2=None, _3=None, l=path_label_hover, a=attr):
                l.text = path_hover_text(a)
            hover_cb = attr.var.trace_add('write', update_hover)
            
            self.trace_data.append((attr.var, button_cb))
            self.trace_data.append((attr.var, hover_cb))
            
            if attr.name == self.parent.focused_test.plot_sim_file:
                sim_cb = attr.var.trace_add('write',
                    lambda _1=None, _2=None, _3=None: self.parent.param_frame.render_sim_frame()
                                   )
                self.trace_data.append((attr.var, sim_cb))
            if attr.name == self.parent.focused_test.plot_mes_file:
                sim_cb = attr.var.trace_add('write',
                    lambda _1=None, _2=None, _3=None: self.parent.param_frame.render_mes_frame()
                                   )
                self.trace_data.append((attr.var, sim_cb))
            
            # place a select button to get a new path
            open_path_button = ttk.Button(frame, text="open",
                    command=lambda attr=attr: self.open_path(attr))
            open_path_button.grid(row=line, column=2)
            
            # add interactibles to a higher scoped list
            self.interactibles.append((open_path_button, path_button))
        
        # boolean attributes are shown as their name and a checkbox
        elif attr.type == 'BOOL':
            # show a check box
            # @TODO the bind not be necessary
            checkbutton = ttk.Checkbutton(frame, variable=attr.var)
            checkbutton.grid(row=line, column=1, cnf=padding_info)
            
            # add the checkbox and variable to a higher scoped list
            # @TODO is attr.var necessary here?
            self.interactibles.append((checkbutton, attr.var))
        
        # if the attribute is a number, show it as a name, an entry, and
        # a unit @TODO error checking on the entry
        elif attr.type == 'NUM':
            # space to enter the user's number
            entry = ttk.Entry(frame, textvariable=attr.var)
            entry.grid(row=line, column=1, cnf=padding_info)
            
            # label containing unit
            unit_label = ttk.Label(frame, text=attr.unit)
            unit_label.grid(row=line, column=2)
            
            # add the entry to a higher scoped list
            # @TODO is attr.var necessary?
            self.interactibles.append((entry, attr.var))
        
        elif attr.type == 'STR':
            # space to enter the user's number
            entry = ttk.Entry(frame, textvariable=attr.var)
            entry.grid(row=line, column=1, cnf=padding_info)
            
            # label containing unit
            unit_label = ttk.Label(frame, text="string")
            unit_label.grid(row=line, column=2)
            
            # add the entry to a higher scoped list
            # @TODO is attr.var necessary?
            self.interactibles.append((entry, attr.var))
        else:
            raise ValueError(f"Incorrect attribute type of '{attr.type}'")
        
    # run the backend PSLF script associated with the focused test's
    # test type
    def run_simulation(self, event=None, save_on_run=True):

        # block running here
        if self.run_sim_active or self.running_thread and self.running_thread.is_alive():
            print("Stop Right There! A PSLF Script is already running.")
            print("Wait until the script has completed to run again.",
                  *[int(i) for i in (self.run_sim_active, bool(self.running_thread), self.running_thread.is_alive())])
                  # prev line for debugging
            ScriptQueue.put(SuperToolMessage('scriptalreadyrunning',
                                "A PSLF Script is already running."))
            return
        
        self.run_sim_active = True
        
        
        if self.parent.focused_test:
            
            print("save_on_run:", save_on_run)
            
            try:
                # print out every variable to terminal
                for k,v in self.parent.focused_test.attrs.items():
                    print(k, v)

                # save project @TODO the choice to run without saving
                if save_on_run:
                    self.parent.save_project()
            # if a parameter is the wrong type or someting like that (float variable
            # is 0.07f for example) then stop before opening pslf
            except tk.TclError as e:
                print()
                traceback.print_exception(e)
                name = v.full_name if v.full_name else k
                print(f"ERROR: Test parameter {name} is not valid. See above error message.")
                self.parent.set_status(f"Test Parameter {name} is not valid. See console for details.", error=True)
                self.run_sim_active = False
                return

            def status_running():
                self.parent.set_status(f"Running {self.parent.focused_test.type} test...", spin=True)
            
            # run script thread
            def run_script():
                # save working directory
                working_dir = os.getcwd()
            
                hide = self.parent.hide_pslf_gui.get()
                last_hide = self.parent.last_hide_pslf_gui_val
                
                try:
                    if last_hide == None:
                        print("last hide == None")
                        kill_pslf()
                        self.parent.focused_test.script(hide)
                        self.parent.set_status("Test completed!")
                    else:
                        
                        if hide and last_hide:
                            print("last hide and hide")
                            # run normally, reuse the terminal
                            
                        if not hide and last_hide:
                            print("last hide and not hide")
                            # kill pslf (in terminal), rerun with gui
                            self.parent.set_status("Restarting PSLF with GUI...", spin=True)
                            kill_pslf()
                            status_running()
                        
                        if hide and not last_hide:
                            print("not last hide and hide")
                            # kill pslf (as gui), rerun in terminal
                            self.parent.set_status("Restarting PSLF without GUI...", spin=True)
                            kill_pslf()
                            status_running()
                            
                        if not hide and not last_hide:
                            print("not last hide and not hide")
                            # double check the window is still open, 
                            def win_enum_handler(hwnd, window_open):
                                name = win32gui.GetWindowText(hwnd)
                                if win32gui.IsWindowVisible(hwnd) and 'pslf' in name.lower():
                                    print("PSLFWindow:", hex(hwnd), name)
                                    window_open.append(name)
                                return True
                            open_windows = []
                            win32gui.EnumWindows(win_enum_handler, open_windows)
                            print("window open:", open_windows)
                            if not open_windows:
                                # if window is closed but process still running, 
                                # kill pslf then rerun with gui
                                self.parent.set_status("Restarting PSLF with GUI...", spin=True)
                                kill_pslf()
                                status_running()
                                
                        self.parent.focused_test.script(hide)
                        self.parent.set_status("Test completed!")
                    
                except SuperToolFatalError as err:
                    print("===== SuperToolFatalError while running Supertool Script - start =====\n")
                    print("=== Working Directory:", os.getcwd())
                    traceback.print_exception(err)
                    print("\n===== SuperToolFatalError while running Supertool Script - end =====")
                    self.parent.set_status("SuperToolFatalError, see console for details.", error=True)
                except Exception as err:
                    print("===== General Exception while running Supertool Script - start =====\n")
                    print("=== Working Directory:", os.getcwd())
                    traceback.print_exception(err)
                    print("\n===== General Exception while running Supertool Script - end =====")
                    self.parent.set_status("General Exception, see console for details.", error=True)
                
                
                self.parent.param_frame.render_sim_frame()
                self.parent.last_hide_pslf_gui_val = hide
                self.run_sim_active = False
                self.unlock_run_button()
                # return to old working directory
                os.chdir(working_dir)
            
            status_running()
            self.running_thread = threading.Thread(target=run_script)
            self.running_thread.start()
            self.lock_run_button()
            
        else:
            # @TODO make this more elegant
            print("No focused test to run a script for!")
            self.parent.set_status("No focused test to run!", error=True)
            self.unlock_run_button()
        
        self.run_sim_active = False
        
        # blah = ' '.join([i.get() for i in self.strings])
        # print(blah)
        # self.parent.set_status("Status Bar: " + blah)
    
    def lock_run_button(self):
        self.run_button.config(state='disabled')
    
    def unlock_run_button(self):
        self.run_button.config(state='normal')
        
    # @TODO change the comments in here oopsie
    def change_focused_test_type(self):
        
        foc = self.parent.focused_test
        
        # create the change type window and make it hold onto focus
        type_prompt_window = tk.Toplevel(self.parent)
        type_prompt_window.transient(self.parent)
        type_prompt_window.grab_set()
        type_prompt_window.focus_force()
        
        # set window title, size, and resizability
        type_prompt_window.title("Change Test Type")
        # @TODO put window in center of parent window
        type_prompt_window.geometry("+500+500")
        type_prompt_window.resizable(False, False)
        
        ## section for putting in single gui elements
        # add test name label
        name_label = ttk.Label(type_prompt_window, text="Test Name: " + foc.name)
        name_label.grid(row=0, column=0, columnspan=2, padx=4, pady=4)
        
        # add test type label
        type_label = ttk.Label(type_prompt_window, text="Test Type")
        type_label.grid(row=1, column=0, padx=4, pady=4)
        
        # add test type interactible combobox (aka dropdown menu)
        type_var = tk.StringVar(type_prompt_window)
        type_dropdown = ttk.Combobox(type_prompt_window, textvariable=type_var)
        test_types = ("Voltage Reference", "Load Reference",
                      "Current Interruption", "Speed Reference",
                      "Steady State", "Synchronization")
        type_dropdown['values'] = test_types
        # set default option to the current type
        type_dropdown.current(test_types.index(foc.type))
        # state = readonly makes it so the user cannot add test types
        type_dropdown.state(['readonly'])
        type_dropdown.grid(row=1, column=1, padx=4, pady=4)
        
        type_dropdown.focus_set()
        
        # create a hidden error label that can pop up when a planned error
        # occurs (such as an empty entry or invalid characters)
        err_label = ttk.Label(type_prompt_window)
        err_label.grid(row=4, column=0, columnspan=2, padx=4, pady=4)
        err_label.grid_remove()
        
        # function called by the create new test button, checks that the
        # name and test entered are valid and  if so creates a new test
        def change_type(event=None):
            if type_var.get() == '':
                err_label.config(text="Select a test type")
                err_label.grid()
            if type_var.get() == foc.type:
                type_prompt_window.destroy()
            else:
                err_label.grid_remove()
                
                # add the test, destroy this window, and update the projectview
                foc.type = type_var.get()
                foc.test_defaults()
                type_prompt_window.destroy()
                self.show_focused_test()
                self.parent.proj_frame.update_test_type(foc)
                self.parent.param_frame.render()
                
                self.parent.set_status(f"Changed type of test '{foc.name}' to {foc.type}.")

        # add a button for creating a new test
        done_button = ttk.Button(type_prompt_window, text="Done",
                                 command=change_type)
        done_button.grid(row=3, column=0, columnspan=2, padx=4, pady=4)
        
        # usability keybinds to make the combobox and button interface
        # more intuitive
        done_button.bind("<Return>", change_type)
        type_dropdown.bind("<Return>", lambda e: type_dropdown.event_generate('<Down>'))
        type_dropdown.bind("<space>", lambda e: type_dropdown.event_generate('<Down>'))
        type_dropdown.bind("<<ComboboxSelected>>", lambda e: done_button.focus())
        
    # @TODO needs typechecking?
    def open_path(self, attr):
        error = True
        if attr.var.get():
            if os.path.exists(attr.get()):
                os.startfile(attr.get())
                printout = f"Starting '{os.path.basename(attr.get())}' in default application."
                error = False
            else:
                if attr.read_only_file:
                    printout = f"File: '{attr.get()}' does not exist. " + \
                          "Select a file using the left button first."
                else:
                    printout = f"File: '{attr.get()}' does not exist. " + \
                          "Run the simulation or select a file " + \
                          "using the left button first."
        else:
            printout = "Open failed. Select a file with the left button first."
        
        print(printout)
        self.parent.set_status(printout, error=error)
    
    # get a new path for path type attributes
    # need to pick between input and output files because the file
    # picker has different behavior depending on if it's saving or
    # opening. uses tkinter.filedialog
    def get_new_path(self, attr):
        if attr.read_only_file:
            path = askopenfilename(
                title=f"Select input {attr.extension.upper()} file",
                defaultextension=f"*.{attr.extension}",
                filetypes=[(f"Input {attr.extension.upper()} File", f"*.{attr.extension}"),
                           ("All Files", "*.*")],
                initialdir=attr.parent.get_dir()
                )
        else:
            path = asksaveasfilename(
                title=f"Choose File Name and Location for Output {attr.extension.upper()} File",
                defaultextension="*.*",
                filetypes=[(f"PSLF Output {attr.extension.upper()} File", f"*.{attr.extension}"),
                           ("All Files", "*.*")],
                initialdir=attr.parent.get_dir()
                )
        
        if path:
            # @TODO make a better decision on backslashes vs slashes OR use pathlib
            rel_path = os.path.relpath(path, attr.parent.get_dir()).replace('\\', '/')
            print(attr.parent.get_dir() + " + " + rel_path)
            attr.var.set(rel_path)
            
            # autofill pslf output file names if they're not already filled in
            if attr.name == "sav_filename":
                attrs = attr.parent.attrs
                for a in attrs.values():
                    if a.type == "PATH" and not a.read_only_file and not a.var.get():
                        path = os.path.basename(attr.var.get())
                        root, ext = os.path.splitext(path)
                        a.var.set(root + "_sim." + a.extension)

def kill_pslf():
    for i in range(10):
        found = False
        for proc in psutil.process_iter():
            try:
                if 'pslf' in proc.name().lower():
                    print(proc.name(), "is getting killed")
                    found = True
                    try:
                        proc.kill()
                    except psutil.AccessDenied:
                        print("AccessDenied while trying to kill PSLF")
                        print("Please wait for PSLF to close or kill it yourself")
                        while True:
                            try:
                                time.sleep(3)
                                proc.kill() # type: ignore
                                break
                            except psutil.AccessDenied:
                                print("Retrying kill")
                            except psutil.NoSuchProcess:
                                break
            except psutil.NoSuchProcess:
                continue
        if not found:
            break

# helper class, used to make pretty separators for the testview scroll frame
class AttributeHeader(ttk.Frame):
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.columnconfigure(2, weight=1)
        
        spacing_frame = ttk.Frame(self)
        spacing_frame.grid(row=0, column=0, sticky='nesw', ipady=2)
        
        self.lsep_frame = ttk.Frame(self, width=20)
        self.lsep_frame.grid(row=1, column=0, sticky='ew', ipadx=6)
        self.lsep_frame.columnconfigure(0, weight=1)
        
        self.lsep = ttk.Separator(self.lsep_frame)
        self.lsep.grid(row=1, column=0, sticky='ew')
        
        self.label = ttk.Label(self, text=text)
        self.label.grid(row=1, column=1, padx=3)

        self.rsep = ttk.Separator(self)
        self.rsep.grid(row=1, column=2, sticky='ew', padx=1)
