# config.py

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory

import json
import os
import threading
import subprocess
import traceback
import time


### step 0: set up window
class SetupWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.minsize(350, 200)
        self.title("Super Tool Setup")
        self.iconphoto(True, tk.PhotoImage(file="./icons/supertoolplay.png"))
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.wrap_length = 345
                
        self.main_frame = ttk.Frame(self, relief="groove", borderwidth=4)
        self.main_frame.grid(sticky='nesw')
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(3, weight=0)
        self.main_frame.columnconfigure(0, weight=1)

        # top bar setup
        self.title_label = ttk.Label(self.main_frame, text="Super Tool Setup", padding='2')
        self.title_label.grid(row=0, column=0, sticky='nw')

        self.top_sep = ttk.Separator(self.main_frame)
        self.top_sep.grid(row=1, column=0, columnspan=5, sticky='new')

        # bottom bar setup
        self.bottom_sep = ttk.Separator(self.main_frame)
        self.bottom_sep.grid(row=3, column=0, columnspan=5, sticky='sew')

        self.left_button = ttk.Button(self.main_frame, text="back", padding='2')
        self.left_button.grid(row=4, column=3, sticky='e')

        self.right_button = ttk.Button(self.main_frame, text="next", padding='2')
        self.right_button.grid(row=4, column=4, sticky='e')

        # first frame setup
        self.frame0 = ttk.Frame(self.main_frame)
        self.frame0.grid(row=2, column=0, columnspan=5, sticky='nesw')
        self.frame0.grid_remove()

        self.welcome_label = ttk.Label(self.frame0,
                text="Welcome to the SuperTool Setup Script.\n\nClick Next to begin.")
        self.welcome_label.grid(row=0, column=0)
        
        # second frame setup
        self.frame1 = ttk.Frame(self.main_frame)
        self.frame1.grid(row=2, column=0, columnspan=5, sticky='nesw')
        self.frame1.grid_remove()
        self.frame1.columnconfigure(0, weight=1)
        
        self.depend_label = ttk.Label(self.frame1,
                text="Resolving dependencies...")
        self.depend_label.grid(row=0, column=0)
        
        self.depend_prog_bar = ttk.Progressbar(self.frame1,
                mode='indeterminate', length=340)
        self.depend_prog_bar.grid(row=1, column=0) #, sticky='ew')
        
        self.depend_done_label = ttk.Label(self.frame1,
                text="Complete! Click Next to continue")
        self.depend_done_label.grid(row=2, column=0)
        self.depend_done_label.grid_remove()
        
        self.depend_done = False
        
        # third frame setup
        
        found_path = self.search_for_veusz()
        print(found_path, "<- found_path")
        
        self.frame2 = ttk.Frame(self.main_frame)
        self.frame2.grid(row=2, column=0, columnspan=5, sticky='nesw')
        self.frame2.grid_remove()
        self.frame2.columnconfigure(0, weight=1)
        
        self.sel_dir_label = ttk.Label(self.frame2,
                text="Select the directory that Veusz is installed in. " + \
                     "If Veusz is not installed, please close this " + \
                     "installer and install Veusz first.", wraplength=self.wrap_length,
                     justify="left")
        self.sel_dir_label.grid(row=0, column=0, columnspan=2)
        
        self.sel_dir_warn_label = ttk.Label(self.frame2, text="",
                wraplength=self.wrap_length)
        self.sel_dir_warn_label.grid(row=3, column=0, columnspan=2)
        
        self.dir_var = tk.StringVar(self.frame2)
        self.dir_var.trace_add('write', self.validate_veusz_path)
        self.dir_var.set(found_path)
        
        self.sel_dir_entry = ttk.Entry(self.frame2, textvariable=self.dir_var, 
                width=42)
        self.sel_dir_entry.grid(row=1, column=0, rowspan=2, sticky='e')
                
        self.sel_dir_button = ttk.Button(self.frame2, text="Select Folder",
                command=self.sel_dir_command)
        self.sel_dir_button.grid(row=1, column=1, sticky='w')
        
        self.sel_dir_reset_button = ttk.Button(self.frame2, text="Reset",
                command=lambda: self.dir_var.set(found_path))
        self.sel_dir_reset_button.grid(row=2, column=1, sticky='e')
        
        # last frame setup
        self.frame3 = ttk.Frame(self.main_frame)
        self.frame3.grid(row=2, column=0, columnspan=5, sticky='nesw')
        self.frame3.grid_remove()
        self.frame3.columnconfigure(0, weight=1)
        
        self.saving_label = ttk.Label(self.frame3, text="Saving Configuration...")
        self.saving_label.grid(row=0, column=0)
        
        self.finished_label = ttk.Label(self.frame3,
                text="Click Finish to complete Super Tool Setup.")
        self.finished_label.grid(row=1, column=0)
        self.finished_label.grid_remove()
        
        # start running for real
        self.show_frame0()


    def show_frame0(self, callee=None):
        if callee:
            callee.grid_remove()
        self.frame0.grid()
        self.title_label.config(text="Installation Start")
        self.left_button.grid_remove()
        self.right_button.config(text="Next >",
                command=lambda: self.show_frame1(self.frame0))

    ### step 1: verify win32 installed (and other pip packages?)
    def show_frame1(self, callee=None):
        if callee:
            callee.grid_remove()
        
        self.frame1.grid()
        self.title_label.config(text="Install Prerequisites")
        self.left_button.grid()
        self.left_button.config(text="< Back",
                command=lambda: self.show_frame0(self.frame1))
        self.right_button.config(text="Next >",
                command=lambda: self.show_frame2(self.frame1))
        
        if self.depend_done:
            self.right_button.config(state='normal')
        else:
            self.left_button.config(state='disabled')
            self.right_button.config(state='disabled')
            self.depend_prog_bar.start()
            
            t = threading.Thread(target=self.depend_process)
            t.start()
            
            
    def depend_process(self):
        try:
            import win32
            time.sleep(0.5)
        except ModuleNotFoundError:
            try:
                subprocess.call("python -m pip install pywin32")
            except PermissionError:
                subprocess.call("python -m pip install --user pywin32")
                
        self.depend_prog_bar.config(mode='determinate', value=100)
        self.depend_prog_bar.stop()
        self.depend_done_label.grid()
        self.left_button.config(state='normal')
        self.right_button.config(state='normal')
        self.depend_done = True
    
    def show_frame2(self, callee=None):
        if callee:
            callee.grid_remove()
        
        self.frame2.grid()
        self.title_label.config(text="Find Veusz Directory")
        self.left_button.config(text="< Back",
                command=lambda: self.show_frame1(self.frame2))
        self.right_button.config(text="Next >",
                command=lambda: self.show_frame3(self.frame2))
        self.validate_veusz_path()
    
    def search_for_veusz(self): 
        keys_to_grab = ["PROGRAMFILES(X86)", "PROGRAMFILES", "APPDATA", "LOCALAPPDATA"]
        env = os.environ.copy()
        for k in keys_to_grab:
            path = env[k]
            dirs_in_path = [d for d in os.scandir(path) if d.is_dir()]
            try:
                for dir in dirs_in_path:
                    if "veusz.exe" in os.listdir(dir.path):
                        return dir.path
            except PermissionError as e:
                pass
        return ''

    def validate_veusz_path(self, a_=None, b_=None, c_=None):
        val = self.dir_var.get()
        if os.path.exists(val):
            try:
                if "veusz.exe" in os.listdir(val):
                    # let the user forward
                    self.sel_dir_warn_label.config(
                        text="The selected directory is valid. Click Next to continue.")
                    self.right_button.config(state='normal')
                else:
                    # block the user from moving forward, tell them veusz.exe isn't in there
                    self.sel_dir_warn_label.config(
                        text="WARNING: veusz.exe does not exist in the selected directory.")
                    self.right_button.config(state='disabled')
            except FileNotFoundError:
                # stop the user, tell them the path doesn't exist
                # this case is for when os turns 'C:\\Program Files '
                # into 'C:\\Program Files' for exists but not for listdir
                self.sel_dir_warn_label.config(
                        text="WARNING: The selected directory does not exist.")
                self.right_button.config(state='disabled')
        else:
            # stop the user, tell them the path doesn't exist
            self.sel_dir_warn_label.config(
                    text="WARNING: The selected directory does not exist.")
            self.right_button.config(state='disabled')
        
    def sel_dir_command(self):
        init_dir = self.dir_var.get()
        if not init_dir or not os.path.exists(init_dir):
            init_dir = "C:\\"

        dir = askdirectory(parent=self, title="Select Veusz's installation directory",
                initialdir=init_dir, mustexist=True)
        if dir:
            # if "veusz.exe" in os.listdir(dir):
            self.dir_var.set(dir.replace("/", "\\"))
        
    def show_frame3(self, callee=None):
        if callee:
            callee.grid_remove()
    
        self.frame3.grid()
        self.title_label.config(text="Complete Installation")
        self.left_button.grid()
        self.left_button.config(text="< Back",
                command=lambda: self.show_frame2(self.frame3))
        self.right_button.config(text="Finish",
                command=self.destroy, state='disabled')
        
        self.saving_label.config(text="Saving Configuration...")
        self.finished_label.grid_remove()
        
        json_dict = {"VEUSZ_PATH" : self.dir_var.get().replace(
                "\\", "/").rstrip(" /")}
        json.dump(json_dict, open('config.json', 'w'), indent=4)
        
        def done():
            self.saving_label.config(text="Configuration Saved!")
            self.finished_label.grid()
            self.right_button.config(state='normal')
            
        self.after(500, done)


### step n: run and clean up
try:
    setup = SetupWindow()
    setup.mainloop()
    time.sleep(2)
    print("Setup Script Complete! Exiting...")
except Exception as e:
    print(traceback.print_exc())
    input("\n\nERROR FOUND! Record it somehow and then Press Enter to close")