# SuperToolGUI.py, Charlie Jordan, 11/15/2023
# main code for mocking up a gui for the super tool program

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import tkinter.font
import tkinter.filedialog  as fd
import json
import os
import webbrowser
import pathvalidate

import supertool.consts as consts
from supertool.SuperToolFrames import BaseOkPopup, StatusBar, Popup
import supertool.SuperToolProject.Project as stproject
import supertool.ScriptListener as ScriptListener
from supertool.pslf_scripts.Super_Tool import ScriptQueue, SuperToolMessage

from supertool.ProjectView import ProjectView
from supertool.TestView import TestView, kill_pslf
from supertool.ParamView import ParamView

class SuperToolGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        ### setup root window
        self.title("Super Tool")
        self.iconphoto(True, tk.PhotoImage(file="./icons/supertoolplay.png"))
        # remove the tear off option from the top menu bar
        self.option_add('*tearOff', tk.FALSE)
        
        # Allows the main frame to be resizeable with the window
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # project is the backend project object that the ui interacts with
        # focused_test is the test to show in the test_view panel
        self.project = stproject.Project()
        self.focused_test = None
        
        self.set_window_title()
        
        # setup backend listener script and its boolean signal flag
        self.running = True
        self.listener = ScriptListener.ScriptListener(self)
        self.listener.start()
        
        # run the helper methods to set up widgets and full window keybinds
        self.styles()
        self.widgets()
        self.keybinds()
        
        # these 2 lines set the minimum size of the window to its initial size
        # @TODO may need to mess with this later but it's fine for now, is update necessary?
        self.update()
        self.minsize(500,250)
        # print(self.winfo_width(), self.winfo_height())
        
        ScriptQueue.put(SuperToolMessage('check4update'))
        
        self.protocol('WM_DELETE_WINDOW', self.on_quit)
        
    # helper method to create relevant styles for the application
    def styles(self):
        
        style = ttk.Style(self)
        
        font = tkinter.font.nametofont(style.lookup('TLabel', 'font'))
        fixed_font = tkinter.font.nametofont('TkFixedFont')
        
        # create style for error labels in the statusbar 
        style.configure('ErrorLabel.TLabel', foreground='red',
            font=(font.cget('family'), font.cget('size'), 'bold'))
        
        # create style for the spinner label 
        style.configure('FixedFont.TLabel', font=fixed_font)
        style.configure('Spinner.TLabel', font=fixed_font)
        
        # create style for hyperlink labels
        style.configure('hyperlink.TLabel', foreground='blue',
            font=(font.cget('family'), font.cget('size'), 'underline'))
        
        # create style for path buttons with paths that don't exist
        style.configure('badpath.TButton', foreground='red',
            font=(font.cget('family'), font.cget('size'), 'bold'))

    # helper method to create and add all of the high level widgets to the 
    # main window. also handles making each row and column resize-able
    def widgets(self):
        ### Frame creation
        self.panedwindow = ttk.PanedWindow(self, orient='horizontal')
        self.panedwindow.grid(row=0, column=0, columnspan=1, rowspan=1, sticky="nesw")
        
        # main frame setup, row and column configure for initial size and resizeability
        # self.grid_rowconfigure(0, minsize=150, weight=1)
        # self.grid_columnconfigure(0, minsize=50, weight=1)
        # self.grid_columnconfigure(1, minsize=50, weight=1)
        self.grid_columnconfigure(0, minsize=50, weight=1)

        # create the sub-frames
        self.proj_frame = ProjectView(self.panedwindow)
        self.test_frame = TestView(self.panedwindow)
        self.param_frame = ParamView(self.panedwindow)
        
        # self.proj_frame.bind("<Configure>", blah)
        
        self.statusbar_frame = StatusBar(self)
        
        # place the sub-frames into the main window
        self.panedwindow.add(self.proj_frame, weight=1)
        self.panedwindow.add(self.test_frame, weight=2)
        self.panedwindow.add(self.param_frame, weight=2)
        # self.proj_frame.grid(row=0,column=0, columnspan=1, rowspan=1, sticky="nesw")
        # self.test_frame.grid(row=0,column=1, columnspan=1, rowspan=1, sticky="nesw")
        # self.param_frame.grid(row=0,column=2, columnspan=1, rowspan=1, sticky="nesw")
        self.statusbar_frame.grid(row=1, column=0, columnspan=1, sticky="nesw")

        # top bar menu setup
        self.menu()

    # helper method to set up main window keybinds
    # @TODO check if these are still active in the plot popup
    def keybinds(self):
        self.bind("<F5>", self.test_frame.run_simulation)
        self.bind("<Control-F5>", lambda e:
            self.test_frame.run_simulation(save_on_run=False))
        self.bind("<Control-o>", self.open_project)
        self.bind("<Control-s>", self.save_project)
        self.bind("<Control-n>", self.new_project)
        self.bind("<Control-S>", self.save_as_project)
        
    # helper method to set up the main file menu at the top of the
    # window. The run menu is also used as a context menu for 
    # test view.
    def menu(self):
        # create and set menu as the applications titlebar menu
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        
        # sub-menu creation
        file_menu = tk.Menu(self.menubar)
        view_menu = tk.Menu(self.menubar)
        self.run_menu = tk.Menu(self.menubar)
        self.graph_menu = tk.Menu(self.menubar)
        help_menu = tk.Menu(self.menubar)
        

        # add options to the file menu
        # accelerators don't actually do anything, they need to be set
        # in the keybinds method
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="ctrl+n")
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator="ctrl+o")
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator="ctrl+s")
        file_menu.add_command(label="Save Project As", command=self.save_as_project, accelerator="ctrl+shift+s")
        file_menu.add_separator()
        # file_menu.add_command(label="New Unit", command=print)
        # file_menu.add_command(label="New Test")
        file_menu.add_command(label="Zip Project", command=self.zip_n_send)
        # file_menu.add_separator()
        # file_menu.add_command(label="Open Workspace", command=open_workspace)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy)

        # add options to the view menu
        view_menu.add_command(label="Sub-Directory Summary", command=self.show_dir_details)

        # add options to the run menu
        self.run_menu.add_command(label="Run", command=self.test_frame.run_simulation, accelerator="F5")
        self.run_menu.add_command(label="Run Without Saving",
            command=lambda: self.test_frame.run_simulation(save_on_run=False),
            accelerator="ctrl+F5")
        self.run_menu.add_separator()
        # tk boolean variable for if pslf should be run with or without its gui
        self.hide_pslf_gui = tk.BooleanVar(value=consts.HIDE_PSLF_GUI)
        self.last_hide_pslf_gui_val = None
        self.run_menu.add_radiobutton(label="Run PSLF with GUI", variable=self.hide_pslf_gui, value=False)
        self.run_menu.add_radiobutton(label="Run PSLF without GUI", variable=self.hide_pslf_gui, value=True)

        # add options to the graph menu
        self.graph_menu.add_command(label="Graph", command=self.param_frame.graph)
        self.graph_menu.add_command(label="Graph Without Saving",
            command=lambda: self.param_frame.graph(save_on_graph=False))

        # add options to the about menu
        help_menu.add_command(label="About", command=self.show_about_popup)
        help_menu.add_command(label="Check For Updates",
            command=lambda: ScriptQueue.put(SuperToolMessage('check4update')))
        
        # add the submenus to the menu bar
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menubar.add_cascade(label="View", menu=view_menu)
        self.menubar.add_cascade(label="Run", menu=self.run_menu)
        self.menubar.add_cascade(label="Graph", menu=self.graph_menu)
        self.menubar.add_cascade(label="Help", menu=help_menu)
    
    # method to call when the program exits
    def on_quit(self):
        def close():
            # set running to false, indicating that the listener thread should stop
            self.running = False
            print("===== Waiting for ScriptListener to finish =====")
            stop_message = SuperToolMessage("stopscriptlistener")
            ScriptQueue.put(stop_message)
            stop_message.wait()
            # queue.join instead of listener because
            # listener.join causes a program freeze
            ScriptQueue.join()
            print("===== ScriptListener has finished  =====", end='')
            
            # close the window
            self.destroy()
            
            # save use pslf gui value
            print("===== Saving Modified Configuration Data =====")
            if self.save_config_data():
                print("===== Modified Configuration Data Saved =====")
            
            # close the pslf window while we're on the way out
            print("===== Closing PSLF =====")
            kill_pslf()
            print("===== PSLF Closed =====")
        
        self.set_status("Closing Super Tool...")
        self.after(5, close)

    def save_config_data(self):
        try:
            consts.config_data['HIDE_PSLF_GUI'] = self.hide_pslf_gui.get()
            json.dump(consts.config_data, 
                    open('config.json', 'w', encoding='utf-8'), indent=4)
            return True
        except FileNotFoundError:
            print("ERROR: Failed to open config.json. Runtime settings not saved.")
            return False

    # wrapper for statusbar text setting
    # needs some work
    def set_status(self, string: str, error: bool=False, spin: bool=False):
        self.statusbar_frame.set_text(string, error=error, spin=spin)

    def update_pane_widths(self):
        # def printout():
        #     print(
        #         f"{self.proj_frame.winfo_width():<5}= "
        #         f"{self.proj_frame.winfo_reqwidth():<5}"
        #         f"{self.test_frame.winfo_width():<5}= "
        #         f"{self.test_frame.winfo_reqwidth():<5}"
        #         f"{self.param_frame.winfo_width():<5}= "
        #         f"{self.param_frame.winfo_reqwidth():<5}"
        #         f"{self.panedwindow.winfo_width():<5}= "
        #         f"{self.panedwindow.winfo_reqwidth():<5}"
        #     )
        
        # printout()
        
        def set_panes():
            # printout()
            
            rw0 = self.proj_frame.winfo_reqwidth()
            rw1 = self.test_frame.winfo_reqwidth()
            rw2 = self.param_frame.winfo_reqwidth()
            
            # w0 = self.proj_frame.winfo_width()
            # w1 = self.test_frame.winfo_width()
            # w2 = self.param_frame.winfo_width()
            
            # nw0 = max(rw0, w0)
            # nw1 = max(rw1, w1)
            # nw2 = max(rw2, w2)
            
            # print(rw0+rw1+rw2+10, w0+w1+w2+10)
            # if nw0+nw1+nw2+10 > w0+w1+w2+10:
            self.panedwindow.config(width=rw0+rw1+rw2+10)
            
            # if nw0+nw1+5 > w0+w1+5:
            self.panedwindow.sashpos(1, rw0+rw1+5)

            # if nw0 > w0:
            self.panedwindow.sashpos(0, rw0)
        
            # printout()

        self.after(150, set_panes)

    # method called by ctrl+n and the file menu
    # shows a prompt asking for a new file name and
    # creates a new project
    # @TODO make the prompt a custom window and institute some error checking
    def _new_project(self, e=None):
        # confirmation and entry popup
        new_project_name = simpledialog.askstring(title="New Project", 
            prompt="Enter a name for the new project.\nAll unsaved progress will be lost.")
        if new_project_name:
            # delete current project class
            del self.project
            self.project = stproject.Project(new_project_name)
            # re-render project pane
            self.proj_frame.render()
            # clear test view
            self.focused_test = None
            self.test_frame.show_focused_test()
            self.param_frame.render()
    
    def new_project(self, e=None):
        new_proj_window = BaseOkPopup(self, "New Project")
        
        name_var = tk.StringVar(self)
        save_var = tk.StringVar(self)
        dir_var = tk.StringVar(self)
        
        def save_select(e=None):
            # save file as dialog
            filename = fd.asksaveasfilename(defaultextension="*.*", filetypes=[("Super Tool Project Files", "*.pec")])
            if filename:
                save_var.set(filename)
        
        def dir_select(e=None):
            dirname = fd.askdirectory(mustexist=True)
            if dirname:
                dir_var.set(dirname)
        
        def ok_command(e=None):
            proj_name = name_var.get()
            save_file = save_var.get()
            work_dir = dir_var.get()
            message_list = []
            
            if proj_name:
                # check for weird characters?
                pass
            else:
                message_list.append("Please enter a name for the project.")
        
            if save_file:
                if not os.path.exists(os.path.dirname(save_file)):
                    message_list.append("Invalid save file path entered")
                elif os.path.isdir(save_file):
                    message_list.append("The entered save file should be a file, not a directory")
                if not pathvalidate.is_valid_filename(os.path.basename(save_file)):
                    message_list.append("The entered save file contains illegal characters for a file name")
            if work_dir:
                if work_dir[-1] in '/\\':
                    work_dir = work_dir[:-1]
                
                if os.path.exists(work_dir):
                    # if it's not a directory, complain
                    if not os.path.isdir(work_dir):
                        message_list.append("The entered working directory is not a directory.")
                else:
                    message_list.append("The entered working directory does not exist.")
            else:
                message_list.append("Please enter a working directory for the project.")
        
            if message_list:
                # update the screen with errors
                new_proj_window.show_errors(message_list)
            else:
                new_proj_window.hide_errors()
            
                # close the new project window
                new_proj_window.destroy()
                
                # delete current project class
                p = stproject.Project(proj_name) # @TODO set work directory and save file name
                p.working_dir = work_dir
                if save_file:
                    p.file_name = save_file
                
                self.set_project(p)
                if save_file:
                    self.save_project()
                
        
        def cancel_command(e=None):
            new_proj_window.destroy()
        
        name_frame = ttk.Frame(new_proj_window.frame)
        name_frame.grid(row=0, sticky='nesw')
        name_frame.columnconfigure(0, weight=1)
        name_frame.columnconfigure(1, weight=1)
        name_label = ttk.Label(name_frame,
                text="Enter a name for the new project.")
        name_label.grid(row=0, column=0, sticky='w')
        name_entry = ttk.Entry(name_frame, textvariable=name_var, width=25)
        name_entry.grid(row=0, column=1, sticky='ew')
        # give the entry keyboard focus
        name_entry.focus_set()
        
        save_frame = ttk.Frame(new_proj_window.frame)
        save_frame.grid(row=1, sticky='nesw')
        save_label = ttk.Label(save_frame,
                text="Enter a save file name for the project.\nLeave blank to choose a save location later.") #, wraplength=225)
        save_label.grid(row=0, column=0, sticky='w', columnspan=2)
        save_entry = ttk.Entry(save_frame, textvariable=save_var, width=45)
        save_entry.grid(row=1, column=0)
        save_select_button = ttk.Button(save_frame, text="Choose File",
                                        command=save_select)
        save_select_button.grid(row=1, column=1, sticky='ew')
        save_select_button.bind("<Return>", save_select)
        
        dir_frame = ttk.Frame(new_proj_window.frame)
        dir_frame.grid(row=2, sticky='nesw')
        dir_label = ttk.Label(dir_frame,
                text="Choose a working directory. The project save file does not need\n" \
                   + "to be inside the working directory, but every file necessary\n" \
                   + "for PSLF (sav, dyd, csv) will need to be there.")
        dir_label.grid(row=0, column=0, sticky='w', columnspan=2)
        dir_entry = ttk.Entry(dir_frame, textvariable=dir_var, width=45)
        dir_entry.grid(row=1, column=0)
        dir_select_button = ttk.Button(dir_frame, text="Choose Folder",
                                       command=dir_select)
        dir_select_button.grid(row=1, column=1, sticky='ew')
        dir_select_button.bind("<Return>", dir_select)
        
        new_proj_window.wrapup(ok_command=ok_command, cancel_command=cancel_command)
        
        
    # method called by ctrl+o and the file menu
    # shows a prompt allowing the user to select a pec file to open
    # then opens the file
    def open_project(self, e=None):
        filename = fd.askopenfilename(filetypes=[("Super Tool Project Files", "*.pec")])
        if filename:
            self.set_status(f"Opening '{os.path.basename(filename)}' ...", spin=True)
            p = stproject.Project()
            p.file_name = filename
            if not p.read_from_file_name():
                self.set_status(f"Opening '{os.path.basename(filename)}' failed!", error=True)
                return
            
            if p.just_unzipped:
                self.set_unzipped_proj(proj=p)
                if p.just_unzipped:
                    self.set_status("Open cancelled.")
                    return
                else:
                    self.set_project(p)
                    self.set_status(f"Opened '{p.title}' Successfully.")
            
            # double check that there's a working directory
            if self.validate_working_dir(proj=p):
                self.set_project(p)
                self.set_status(f"Opened '{p.title}' Successfully.")
            else:
                self.set_status("Open cancelled.")
            
    def set_project(self, proj):
        del self.project
        self.project = proj
        # set window title
        self.set_window_title()
        # re-render project pane
        self.proj_frame.render()
        self.proj_frame.update_proj_header()
        # clear test view
        self.focused_test = None
        self.test_frame.show_focused_test()
        self.param_frame.render()
        self.update_pane_widths()
    
    def set_window_title(self):
        text = f"Super Tool {consts.VERSION} - {self.project.title}"
        if self.project.file_name:
            text += f" ({self.project.file_name})"
        
        self.title(text)
    
    def show_dir_details(self):
        s = tk.Toplevel(self)
        
        lines = [
            "Summary of Sub Directories\n",
            "The projects directory structure is shown below. It should be useful for debugging",
            "structural issues with your project's subdirectories. Each pair of lines contains ",
            "a first line, holding the deepest level of the Project ; Unit ; Test structure that",
            "is available. The second line in the pair is those stucture's sub-directories, sep-",
            "-arated by ' -> ' strings. The . and .. sub-directories mean 'current directory' and",
            "'parent directory', respectively. These linesshould be compared to your actual system",
            "files, and then use the context menu in the project pane to modify directories",
            "accordingly. The 'tree' command in your terminal or the left pane in file explorer",
            "may be useful.\n",
            "Example:",
            "ProjectName ; UnitName ; TestName",
            "\tC:/MyDir -> my unit's directory -> test dir\n"
        ]
        p1 = f"{self.project.title}"
        p2 = f"\t{self.project.working_dir}"
        if self.project.units:
            for u_name, unit in self.project.units.items():
                u1 = p1 + f" ; {u_name}"
                u2 = p2 + f" -> {max('.', unit.sub_dir)}"
                if unit.tests:
                    for t_name, test in unit.tests.items():
                        t1 = u1 + f" ; {t_name}"
                        t2 = u2 + f" -> {max('.', test.sub_dir)}"
                        lines.append(t1)
                        lines.append(t2)
                        # for a_name, attr in test.attrs.items():
                        #     pass
                else:
                    lines.append(u1)
                    lines.append(u2)
                    
        else:
            lines.append(p1)
            lines.append(p2)
        label = ttk.Label(s, text="\n".join(lines), padding=4)
        label.pack()
        
    # method called in project view
    # shows a prompt for the user to rename the currently open project
    def rename_project(self, e=None):
        # entry popup
        new_project_name = simpledialog.askstring(title="Rename Project",
            prompt=f"Enter a new project name to replace\n{self.project.title}.")
        if new_project_name:
            self.set_status(f"Renaming '{self.project.title}'")
            # set the project name
            old_project_name = self.project.title
            self.project.title = new_project_name
            
            # change project header in project pane
            self.proj_frame.update_proj_header()
            
            # set window title
            self.set_window_title()
            
            self.set_status(f"Renamed '{old_project_name}' to '{self.project.title}'.")

    def validate_working_dir(self, proj=None):
        if not proj:
            proj = self.project
        if not proj.working_dir or \
                not os.path.exists(proj.working_dir):
            messagebox.showinfo(title="Invalid Working Directory",
                message="This project does not have a valid working directory\n" +
                    "You need to set a working directory first.\n" + \
                    "The next window will walk you through that process.")
            self.prompt_for_new_working_dir(proj=proj)
        return bool(proj.working_dir)
        
    def set_unzipped_proj(self, proj: stproject.Project):
        win = BaseOkPopup(self, title="Setup Imported Project")
        win.frame.columnconfigure(0, weight=1)
        
        explain_label = ttk.Label(win.frame, wraplength=350,
                text="It looks like this project file was recently unzipped. "
                     "Use this window to get it set up on your system.")
        explain_label.grid(row=0, column=0, columnspan=2)
        
        explain_label2 = ttk.Label(win.frame, wraplength=350,
                text=f"The working directory for project {proj.title} is likely"
                     f" a directory named '{os.path.basename(proj.working_dir)}'"
                      ". Select the working directory below.")
        explain_label2.grid(row=1, column=0, columnspan=2)
        
        dir_var = tk.StringVar(win.frame)
        # set dir var
        working_dir_base = os.path.basename(proj.working_dir)
        proj_file_name_dir = os.path.dirname(proj.file_name)
        if working_dir_base in os.listdir(proj_file_name_dir):
            dir_var.set(os.path.normpath(
                os.path.join(proj_file_name_dir, working_dir_base)
            ))
        
        
        def dir_select():
            dirname = fd.askdirectory(mustexist=True,
                    initialdir=os.path.dirname(proj.file_name))
            if dirname:
                # @TODO add a printout of the number of paths that are valid from
                # choosing a new directory. maybe add a verify button?
                dir_var.set(dirname)
        
        dir_entry = ttk.Entry(win.frame, textvariable=dir_var, width=45)
        dir_entry.grid(row=2, column=0)
        
        dir_select_button = ttk.Button(win.frame, text="Choose Folder",
                                       command=dir_select)
        dir_select_button.grid(row=2, column=1, sticky='ew')
        dir_select_button.bind("<Return>", lambda e: dir_select())
        
        def ok_command():
            work_dir = dir_var.get()
            message_list = []
            
            if work_dir:
                if work_dir[-1] in '/\\':
                    work_dir = work_dir[:-1]
                
                if os.path.exists(work_dir):
                    # if it's not a directory, complain
                    if not os.path.isdir(work_dir):
                        message_list.append("The entered working directory is not a directory.")
                else:
                    message_list.append("The entered working directory does not exist.")
            else:
                message_list.append("Please Select the working directory")
        
            if message_list:
                win.show_errors(message_list)
            else:
                win.hide_errors()
        
                proj.working_dir = work_dir
                proj.just_unzipped = 0
                
                win.destroy()
                
                self.set_status(f"Working directory changed to '{os.path.normpath(self.project.get_dir())}'.")
        
        def cancel_command():
            win.destroy()
        
        if proj.just_unzipped & 2:
            outside_label = ttk.Label(win.frame, wraplength=350,
                    text="This project has some files that were not in the working directory "
                    "of the project when it was compressed. These files are stored in the "
                    "\"outside_working_dir\" folder, which should now be in the working "
                    "directory for this project. Reorganize these files as you see fit.")
            outside_label.grid(row=3, column=0, columnspan=2)
        
        win.wrapup(ok_command, cancel_command)
        
    def prompt_for_new_working_dir(self, e=None, proj=None):
        
        if proj is None:
            proj = self.project
        
        set_dir_window = BaseOkPopup(self, title="Choose a new working directory")
        
        dir_var = tk.StringVar(self, value=proj.working_dir)
        
        def dir_select():
            dirname = fd.askdirectory(mustexist=True, initialdir=self.project.working_dir)
            if dirname:
                # @TODO add a printout of the number of paths that are valid from
                # choosing a new directory. maybe add a verify button?
                dir_var.set(dirname)
        
        def ok_command(proj=proj):
            work_dir = dir_var.get()
            message_list = []
            
            if work_dir:
                if work_dir[-1] in '/\\':
                    work_dir = work_dir[:-1]
                
                if os.path.exists(work_dir):
                    # if it's not a directory, complain
                    if not os.path.isdir(work_dir):
                        message_list.append("The entered working directory is not a directory.")
                else:
                    message_list.append("The entered working directory does not exist.")
            else:
                message_list.append("Please enter a working directory for the project.")
        
            if message_list:
                # update the screen with errors
                set_dir_window.show_errors(message_list)
            else:
                set_dir_window.hide_errors()
            
                # close the new project window
                set_dir_window.destroy()
                
                print(proj.__repr__())
                print(self.project.__repr__())
                
                if work_dir != proj.working_dir:
                    proj.working_dir = work_dir
                    if proj != self.project:
                        self.set_project(proj)
                self.proj_frame.update_proj_header()
                if self.focused_test:
                    # rerender focused test to update hovertext @TODO do it better
                    self.test_frame.show_focused_test()
                
                self.set_status(f"Working directory changed to '{os.path.normpath(self.project.get_dir())}'.")
        
        def cancel_command():
            set_dir_window.destroy()
        
        dir_label = ttk.Label(set_dir_window.frame,
                text="Choose a new working directory. The project save file does not need\n" \
                   + "to be inside the working directory, but every file necessary\n" \
                   + "for PSLF (sav, dyd, csv) will need to be there.")
        dir_label.grid(row=0, column=0, sticky='w', columnspan=2)
        
        dir_entry = ttk.Entry(set_dir_window.frame, textvariable=dir_var, width=45)
        dir_entry.grid(row=1, column=0)
        dir_entry.bind('<Return>', lambda e: ok_command())
        
        dir_select_button = ttk.Button(set_dir_window.frame, text="Choose Folder",
                                       command=dir_select)
        dir_select_button.grid(row=1, column=1, sticky='ew')
        dir_select_button.bind("<Return>", lambda e: dir_select())
        
        set_dir_window.wrapup(ok_command=ok_command, cancel_command=cancel_command)

    # method called by ctrl+shift+s and the file menu
    # shows a prompt allowing the user to save to a pec file
    def save_project(self, e=None):
        self.set_status("Saving...", spin=True)
        self.save_config_data()
        if self.project.file_name:
            self.project.write_to_file_name()
        else:
            self.save_as_project()
        self.set_status(f"Saved '{self.project.title}' to {self.project.file_name}")

    # method called by ctrl+shift+s and the file menu
    # shows a prompt allowing the user to save to a pec file
    def save_as_project(self, e=None):
        filename = fd.asksaveasfilename(defaultextension="*.*", filetypes=[("Super Tool Project Files", "*.pec")])
        if filename:
            self.project.file_name = filename
            self.save_project()

    def zip_n_send(self):
        zip_n_send_window = BaseOkPopup(self, title="Zip Project")
        
        explanation_label = ttk.Label(zip_n_send_window.frame,
                text="This will package up all of the required files in your "
                     "project into a zip file, which you can then send to "
                     "someone else with Super Tool for them to use.",
                wraplength=400)
        explanation_label.grid(row=0, column=0, columnspan=2)
        
        choose_file_label = ttk.Label(zip_n_send_window.frame,
                text="Select a location and name for the zip file.")
        choose_file_label.grid(row=1, column=0, columnspan=1)

        def choose_file():
            filename = fd.asksaveasfilename(initialdir=os.path.dirname(self.project.file_name),
                    defaultextension="*.*",
                    filetypes=[("Zip File", "*.zip"), ("All Files", "*.*")])
            if filename:
                file_var.set(filename)
        choose_file_button = ttk.Button(zip_n_send_window.frame,
                text="Select File", command=choose_file)
        choose_file_button.grid(row=1, column=1)
        
        file_init_val = os.path.splitext(self.project.file_name)[0]
        if file_init_val:
            file_init_val += ".zip"
        file_var = tk.StringVar(master=zip_n_send_window.frame,
                value=file_init_val)
        choose_file_entry = ttk.Entry(zip_n_send_window.frame,
                textvariable=file_var, width=60)
        choose_file_entry.grid(row=2, column=0, columnspan=2)
        
        opt_label_frame = ttk.LabelFrame(zip_n_send_window.frame, text="Options")
        opt_label_frame.grid(row=3, column=0, sticky='nesw', columnspan=2)
        opt_label_frame.columnconfigure(0, weight=1)
        opt_label_frame.columnconfigure(1, weight=1)
        
        # checkboxes for various options
        include_all_label = ttk.Label(opt_label_frame,
                text="Include all files in working directory, not just files "
                     "necessary to run the tool.", wraplength=350)
        include_all_label.grid(row=0, column=1, sticky='w')
        include_all_checkbox = ttk.Checkbutton(opt_label_frame)
        include_all_checkbox.grid(row=0, column=0)
        include_all_checkbox.state(['!alternate']) # set as disabled
        
        path_on_clipboard_label = ttk.Label(opt_label_frame,
                text="Copy zip file to clipboard for easy emailing",
                wraplength=350)
        path_on_clipboard_label.grid(row=1, column=1, sticky='w')
        path_on_clipboard_checkbox = ttk.Checkbutton(opt_label_frame)
        path_on_clipboard_checkbox.grid(row=1, column=0)
        path_on_clipboard_checkbox.state(['selected', '!alternate']) # set active
        
        for child in opt_label_frame.children.values():
            child.grid_configure(pady=4)
        
        def ok_command():
            zip_name = file_var.get()
            include_all = 'selected' in include_all_checkbox.state()
            path_on_clipboard = 'selected' in path_on_clipboard_checkbox.state()
            message_list = []
            
            if zip_name:
                if os.path.exists(os.path.dirname(zip_name)):
                    if not pathvalidate.is_valid_filename(os.path.basename(zip_name)):
                        message_list.append("The entered zip file contains illegal characters for a file name")
                
                    root, ext = os.path.splitext(os.path.basename(zip_name))
                    if not root:
                        message_list.append("Enter a file name before the extension. (eg. file.zip)")
                    if not ext:
                        message_list.append("The zip file needs an extenstion! (eg. file.zip)")
                else:
                    message_list.append("The zip file needs to be created in an existing folder.")
            else:
                message_list.append("Please enter a zip file name.")
            
            if message_list:
                zip_n_send_window.show_errors(message_list)
            else:
                zip_n_send_window.hide_errors()
                zip_n_send_window.destroy()
                print(zip_name, include_all)
                self.set_status(f"Creating zip file: {zip_name}.", spin=True)
                
                def compress_func():
                    complete = self.project.compress(zip_name, include_all)
                    if complete:
                        if path_on_clipboard:
                            win_zip_name = zip_name.replace("/", "\\")
                            os.system(f"powershell Set-Clipboard -Path '{win_zip_name}'")
                        
                        self.set_status(f"Project compressed to {zip_name}.")
                        
                    else:
                        self.set_status(f"Compressing project to {zip_name} failed."
                                        " See console for details.")
                
                ScriptQueue.put(SuperToolMessage("compress", data=compress_func))
                
        
        def cancel_command():
            zip_n_send_window.destroy()
        
        zip_n_send_window.wrapup(ok_command, cancel_command)

    def show_about_popup(self):
        win = Popup(self, title="About")
        
        title_label = ttk.Label(win, text="Super Tool GUI")
        title_label.grid(row=0, column=0)
        
        version_label = ttk.Label(win, text=f"Version: {consts.VERSION}")
        version_label.grid(row=1, column=0)
        
        link_label = ttk.Label(win, text="Project Website", cursor="hand2",
                style='hyperlink.TLabel')
        link_label.grid(row=2, column=0)
        link_label.bind("<1>", 
                lambda e: webbrowser.open_new_tab(
                    consts.GITHUB_REPO.split('releases', maxsplit=1)[0]
                    ))
        
        ok_button = ttk.Button(win, text="OK", command=win.destroy)
        ok_button.grid(row=3, column=0)

        for widget in win.winfo_children():
            widget.grid_configure(padx=5, pady=3)
