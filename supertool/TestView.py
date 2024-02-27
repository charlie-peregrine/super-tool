# TestView.py, Charlie Jordan, 12/5/2023
# file to store the gui work for the test pane of the UI

import signal
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

import PSLF_PYTHON

from supertool.SuperToolFrames import ScrollFrame
from supertool.pslf_scripts.Super_Tool import SuperToolFatalError

# Frame subclass for presenting and receving info regarding
# individual tests and their attributes
class TestView(ttk.Frame):
    def __init__(self, parent):
        # set up the frame and place it in the window
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                            height=100, width=100)
        
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
        self.run_button_hover = Hovertip(self.run_button, hover_delay=300,
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
        
        self.thread_running = False
        
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
        
        style = ttk.Style()
        
        # create style for path buttons with paths that don't exist 
        button_font = tkinter.font.nametofont(style.lookup('TButton', 'font'))
        style.configure('badpath.TButton', foreground='red',
            font=(button_font.cget('family'), button_font.cget('size'), 'bold'))
        
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
            
            # self.sub_dir_label = ttk.Label(self.frame, text="Sub-Directory")
            # self.sub_dir_label.grid(row=2, column=0)
            # self.sub_dir_val_label = ttk.Label(self.frame,
            #         text=focused.sub_dir + "haaa", wraplength=40)
            # print("sub dir:", focused.sub_dir)
            # self.sub_dir_val_label.grid(row=2, column=1)
            # self.sub_dir_button = ttk.Button(self.frame,
            #         text="Change")
            # self.sub_dir_button.grid(row=2, column=2)
            
            # set up for loop, offset is how many rows down the big
            # list of attributes should start
            keys = list(focused.attrs.keys())
            offset = 2
            
            # storage for all of the interactibles so they still
            # work outside of the loop
            self.interactibles = []
            
            # for every attribute of the attribute dictionary, add
            # a line containing its name and relevant input fields
            for i in range(len(keys)):
                attr = focused.attrs[keys[i]]
                
                # paths are shown with their name, their short name,
                # and a button to open a file picker window. hovering
                # over the short name shows a tooltip of the full path name
                if attr.type == 'PATH':
                    # attribute name shown
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
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
                    
                    path_button = ttk.Button(self.frame, text=short_name(attr.var.get()),
                            command=lambda attr=attr: self.get_new_path(attr))
                    path_button.grid(row=i+offset, column=1, sticky='nesw')
                    
                    def clear_path(e=None, attr=attr):
                        attr.var.set("")
                    path_button.bind("<3>", clear_path)
                    
                    # create hovertext for paths to show the long path instead of just the basename
                    def path_hover_text(attribute):
                        if attribute.var.get() == '':
                            return "Click to Select a file"
                        else:
                            print(attribute.get())
                            print("RO:", attribute.read_only_file, end=' - ')
                            if attribute.read_only_file:
                                # check that the file itself exists
                                print(attribute.get())
                                print(os.path.exists(attribute.get()))
                                if not os.path.exists(attribute.get()):
                                    return f"This file does not exist at this location.\n" + \
                                           f"Full Path: {attribute.get()}\n" + \
                                           f"Relative Path: {attribute.var.get()}\n" + \
                                            "Right click to clear or click to re-select a file" 
                            else:
                                # check that the parent directory exists
                                print(attribute.parent.get_dir())
                                print(os.path.exists(os.path.dirname(attribute.get())))
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
                    path_label_hover = Hovertip(path_button, path_hover_text(attr), hover_delay=300)
                    
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
                    
                    # place a select button to get a new path
                    open_path_button = ttk.Button(self.frame, text="open",
                            command=lambda attr=attr: self.open_path(attr))
                    open_path_button.grid(row=i+offset, column=2)
                    
                    # add interactibles to a higher scoped list
                    self.interactibles.append((open_path_button, path_button))
                
                # boolean attributes are shown as their name and a checkbox
                elif attr.type == 'BOOL':
                    # attribute name shown
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    # show a check box
                    # @TODO the bind not be necessary
                    checkbutton = ttk.Checkbutton(self.frame, variable=attr.var)
                    checkbutton.grid(row=i+offset, column=1)
                    
                    # add the checkbox and variable to a higher scoped list
                    # @TODO is attr.var necessary here?
                    self.interactibles.append((checkbutton, attr.var))
                
                # if the attribute is a number, show it as a name, an entry, and
                # a unit @TODO error checking on the entry
                elif attr.type == 'NUM':
                    # show the name
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    # space to enter the user's number
                    entry = ttk.Entry(self.frame, textvariable=attr.var)
                    entry.grid(row=i+offset, column=1)
                    
                    # label containing unit
                    unit_label = ttk.Label(self.frame, text=attr.unit)
                    unit_label.grid(row=i+offset, column=2)
                    
                    # add the entry to a higher scoped list
                    # @TODO is attr.var necessary?
                    self.interactibles.append((entry, attr.var))
                
                elif attr.type == 'STR':
                    # show the name
                    title_label = ttk.Label(self.frame, text=attr.name)
                    title_label.grid(row=i+offset, column=0, sticky='w')
                    
                    # space to enter the user's number
                    entry = ttk.Entry(self.frame, textvariable=attr.var)
                    entry.grid(row=i+offset, column=1)
                    
                    # label containing unit
                    unit_label = ttk.Label(self.frame, text="string")
                    unit_label.grid(row=i+offset, column=2)
                    
                    # add the entry to a higher scoped list
                    # @TODO is attr.var necessary?
                    self.interactibles.append((entry, attr.var))
                else:
                    raise ValueError(f"Incorrect attribute type of '{attr.type}'")
                    
            
            # if focused.plot_sim_file:
            #     attr = focused.attrs[focused.plot_sim_file]
            #     trace = attr.var.trace_add('write', lambda a_, b_, c_:
            #         self.parent.param_frame.show_simulated_headers())
            #     self.trace_data.append((attr.var, trace))
                
        else:
            # if there's no focused test, show that no test is selected
            # @TODO probably a memory leak due to dropping the old no_test_label
            self.no_test_label = ttk.Label(self.frame, text="No Test Selected. Create or click one to begin.")
            self.no_test_label.grid(row=1,column=0)
        
    # run the backend PSLF script associated with the focused test's
    # test type
    def run_simulation(self, event=None, save_on_run=True):

        # block running here
        if self.thread_running:
            print("Stop Right There! A PSLF Script is already running.")
            print("Wait until the script has completed to run again.")
            return
        
        self.thread_running = True
        self.run_button.config(state='disabled')
        
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
                print("ERROR: A test parameter is not valid. See above error message.")
                return

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
                    else:
                        
                        if hide and last_hide:
                            print("last hide and hide")
                            # run normally, reuse the terminal
                            
                        if not hide and last_hide:
                            print("last hide and not hide")
                            # kill pslf (in terminal), rerun with gui
                            kill_pslf()
                        
                        if hide and not last_hide:
                            print("not last hide and hide")
                            # kill pslf (as gui), rerun in terminal
                            kill_pslf()
                            
                        if not hide and not last_hide:
                            print("not last hide and not hide")
                            # double check the window is still open, 
                            def winEnumHandler(hwnd, window_open):
                                name = win32gui.GetWindowText(hwnd)
                                if win32gui.IsWindowVisible(hwnd) \
                                    and 'pslf' in name.lower():
                                        print("PSLFWindow:", hex(hwnd), name)
                                        window_open.append("name")
                                return True
                            open_windows = []
                            win32gui.EnumWindows(winEnumHandler, open_windows)
                            print("window open:", open_windows)
                            if open_windows == "":
                                # if window is closed but process still running, 
                                # kill pslf then rerun with gui
                                kill_pslf()
                                
                        self.parent.focused_test.script(hide)
                    
                    
                except SuperToolFatalError as err:
                    print("===== SuperToolFatalError while running Supertool Script - start =====\n")
                    print("=== Working Directory:", os.getcwd())
                    traceback.print_exception(err)
                    print("\n===== SuperToolFatalError while running Supertool Script - end =====")
                except Exception as err:
                    print("===== General Exception while running Supertool Script - start =====\n")
                    print("=== Working Directory:", os.getcwd())
                    traceback.print_exception(err)
                    print("\n===== General Exception while running Supertool Script - end =====")
                
                self.parent.last_hide_pslf_gui_val = hide
                self.thread_running = False
                self.run_button.config(state='normal')
                # return to old working directory
                os.chdir(working_dir)
            
            runner_thread = threading.Thread(target=run_script)
            runner_thread.start()
            
            
            
        else:
            # @TODO make this more elegant
            print("No focused test to run a script for!")
        # blah = ' '.join([i.get() for i in self.strings])
        # print(blah)
        # self.parent.set_status("Status Bar: " + blah)
    
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
        test_types = ("Voltage Reference", "Load Reference", "Current Interruption", "Speed Reference", "Steady State")
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
        
        
    # @TODO needs typechecking
    def open_path(self, attr):
        if attr.var.get():
            os.startfile(attr.get())
        else:
            print("No file to open!!!! uh oh")
    
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
            # @TODO make this include the test subdirectory
            # @TODO make a better decision on backslashes vs slashes
            rel_path = os.path.relpath(path, attr.parent.get_dir()).replace('\\', '/')
            print(attr.parent.get_dir() + rel_path)
            attr.var.set(rel_path)
            if attr.name == self.parent.focused_test.plot_sim_file:
                self.parent.param_frame.render_sim_frame()
            if attr.name == self.parent.focused_test.plot_mes_file:
                self.parent.param_frame.render_mes_frame()

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
