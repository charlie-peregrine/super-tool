# ProjectView.py, Charlie Jordan, 11/28/2023
# Contains the frame for the project panel and
# all of its derivatives

import os
import tkinter as tk
from tkinter import ttk
# @TODO replace messagebox and simpledialog with more robust windows
from tkinter import messagebox
from tkinter import simpledialog
import tkinter.filedialog  as fd
from idlelib.tooltip import Hovertip

import supertool.consts as consts
from supertool.SuperToolFrames import *

# subclass of frame, used to hold a nested visual structure of the
# underlying SuperToolProject object, and allow the user to manipulate
# the project with right click context menus
class ProjectView(ttk.Frame):
    def __init__(self, parent):

        # set up frame
        super().__init__(parent, borderwidth=5, relief='groove',
                    height=300, width=300)
        self.parent = parent.master

        # grab project for easier access
        self.proj = self.parent.project

        # the row and column configures allow for the scrollbar
        # frame and label section to resize correctly
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        # @TODO font size up of header
        self.proj_header = ttk.Label(self, text=self.proj.title)
        self.proj_header.grid(row=0, column=0, columnspan=3, sticky='w')

        # project header label change menu
        self.proj_header_menu = tk.Menu(self.proj_header)
        self.proj_header.bind('<3>',
                lambda e: self.proj_header_menu.post(e.x_root, e.y_root))
        self.proj_header_menu.add_command(label="Rename Project",
                command=self.parent.rename_project)
        self.proj_header_menu.add_command(label="New Project",
                command=self.parent.new_project)
        self.proj_header_menu.add_command(label="Change Working Directory",
                command=self.parent.prompt_for_new_working_dir)
        
        self.proj_header_hover = Hovertip(self.proj_header,
                text="Working directory: " + self.proj.working_dir, hover_delay=consts.HOVER_DELAY)

        # make a right click menu for the unit labels
        self.unit_context_menu = tk.Menu(self)
        # add commands to the context menu
        self.unit_context_menu.add_command(label="delete unit",
                        command=self.delete_unit)
        self.unit_context_menu.add_command(label="rename unit",
                        command=self.rename_unit)
        self.unit_context_menu.add_command(label="change unit sub-dir",
                            command=self.set_unit_sub_dir)
        self.unit_context_menu.add_command(label="new unit",
                        command=self.add_unit)
        self.unit_context_menu.add_command(label="new test",
                        command=self.add_test_from_unit)

        # create context menu for tests
        self.test_context_menu = tk.Menu(self)
        self.test_context_menu.add_command(label="delete test",
                            command=self.delete_test)
        self.test_context_menu.add_command(label="rename test",
                            command=self.rename_test)
        self.test_context_menu.add_command(label="change test sub-dir",
                            command=self.set_test_sub_dir)
        self.test_context_menu.add_command(label="new test",
                            command=self.add_test_from_test)

        # add scrollbar frame for the project section
        self.scroller = ScrollFrame(self)
        self.scroller.grid(row=1, column=0, sticky='nesw')

        # dummy_label is here so clicked_widget doesn't throw type errors
        # in vscode
        self.dummy_label = ttk.Label(self)

        # render the project pane
        self.render()

    # helper method to re-render the project panel, used for when the
    # backend project object changes
    def render(self):
        # reset self.proj in case the project object got changed
        self.proj = self.parent.project

        # keep the visible project header up to date
        self.proj_header.config(text=self.proj.title)

        # grab the scroller's frame for easier access
        frame = self.scroller.frame

        # clear the scroller frame if there's anything in it
        for widget in frame.winfo_children():
            widget.destroy()

        # reset the clicked_widget to dummy_label
        self.clicked_widget = self.dummy_label
        
        # main block for rendering the nested project structure
        # nesting is handled through padding in tkinter's frames primarily
        if self.proj.units:
            # iterate through each unit in the dictionary
            # @TODO sort the units better
            for unit_key in sorted(self.proj.units.keys()):
                unit = self.proj.units[unit_key]
                
                # each unit has a frame that it and its tests live in
                unit_frame = self.build_unit_frame(unit, frame)
                unit.frame = unit_frame

                # show all of the unit's tests
                if unit.tests:
                    # iterate through the tests and show them
                    # @TODO sort the tests better
                    for test_key in sorted(unit.tests.keys()):

                        test = unit.tests[test_key]

                        # every test lives in a frame that house it and its
                        # type label
                        test_frame = self.build_test_frame(test, unit_frame)
                        test.frame = test_frame
                
        else:
            # show no units if there are no units
            self.show_no_units()

    def show_no_units(self):
        self.no_unit_sep = ttk.Separator(
            self.scroller.frame, orient='horizontal')
        self.no_unit_label = ttk.Label(
            self.scroller.frame, text="No Units")
        self.no_unit_sep.pack(fill='x')
        self.no_unit_label.pack(padx=10, anchor='w')

        # right clicking on no units allows the user to add a unit
        unit_label_menu = tk.Menu(self.no_unit_label)
        def right_click_unit(e):
            self.clicked_widget = e.widget
            unit_label_menu.post(e.x_root, e.y_root)

        self.no_unit_label.bind("<3>", right_click_unit)
        unit_label_menu.add_command(label="new unit",
                        command=self.add_unit)

    def build_unit_frame(self, unit, parent_frame):
        unit.sep = ttk.Separator(parent_frame, orient='horizontal')
        unit.sep.pack(fill='x')
        #   ^ using pack here since everything is in a single column
        
        # frame_index = len(parent_frame.children)
        # print(frame_index)
        unit_frame = ttk.Frame(parent_frame, padding='10 0 0 4', 
                name=f'!unitframe{hash(unit.name)}')
        unit_frame.pack(fill='x')

        # the unit_label shows the name of the unit
        # it is also how units are looked up for left and
        # right click actions, so be very careful if changing the
        # widget hierarchy and labeling of the units and tests
        unit_label = ttk.Label(unit_frame, text=unit.name)
        unit_label.pack(anchor='w')
        
        unit.hovertext = Hovertip(unit_label, text="Sub Directory: " + unit.sub_dir, hover_delay=consts.HOVER_DELAY)

        # internal helper function that sets the clicked_widget
        # and triggers the unit_label_menu to be posted
        def right_click_unit(e):
            self.clicked_widget = e.widget
            self.unit_context_menu.post(e.x_root, e.y_root)

        # right click calls right_click_unit, effectively
        # saving the right clicked widget and posting the unit
        # context menu. This is necessary because of a
        # lexing/scoping issue with context menus and commands
        # with arguments
        for widget in (*unit_frame.children.values(), unit_frame):
            widget.bind("<3>", right_click_unit)

        unit.no_tests_label = ttk.Label(unit_frame, text="No Tests")
        if not unit.tests:
            # if there aren't any tests then say so
            unit.no_tests_label.pack(anchor='w', padx=10)

            # @TODO add right click on the no tests label back.
            # currently it only works with one of the test_label_menus
            # test_label_menu = tk.Menu(test_label)
            # def right_click_test(e):
            #     self.clicked_widget = e.widget
            #     test_label_menu.post(e.x_root, e.y_root)

            # test_label.bind("<3>", lambda e: right_click_test(e))
            # test_label_menu.add_command(label="new test",
            #                     command=self.add_test_from_no_test)
        
        return unit_frame

    def build_test_frame(self, test, parent_frame):
        test_frame = ttk.Frame(parent_frame, padding="10 0 0 0",
                borderwidth=2, name=f'!testframe{hash(test.name)}')
        test_frame.pack(fill='x')
        
        # same warning as with units, be very careful when
        # changing the hierarchy and names of the test labels
        # and frames
        test_label = ttk.Label(test_frame, text=test.name)
        test_label.pack(padx=0, anchor='w')

        # right_click_test works the same as right_click_unit
        def right_click_test(e):
            self.clicked_widget = e.widget
            self.test_context_menu.post(e.x_root, e.y_root)

        test.hovertext = Hovertip(test_label, text="Sub Directory: " + test.sub_dir, hover_delay=consts.HOVER_DELAY)
        
        # add the type label of the test to the test frame
        test_type_label = ttk.Label(test_frame, text=test.type)
        test_type_label.pack(padx=10, anchor='w')
        
        for widget in (*test_frame.children.values(), test_frame):
            # left clicking on a test focuses the test, showing its
            # details and attributes in the testview frame
            widget.bind("<1>", self.focus_test)

            # right clicking a test runs the right_click_test
            # method with the added commands in it
            widget.bind("<3>", right_click_test)
        
        return test_frame

    # returns the test or unit object in the project object tree
    # correlating to the widget that the user clicked on (should be a label)
    # defaults to self.clicked_widget
    def get_clicked_test_or_unit(self, widg=None):
        if widg is None:
            widg = self.clicked_widget

        # print("\n======================================")
        # print("clicked widget:", widg)
        # print("masters' children:", len(widg.master.children))
        # for L, c in widg.master.children.items():
        #     print(f"{L:<15}{c}")
        # print("=======================================")

        # search up the widget hierarchy for the canvas widget holding the
        # selected widget, storing each preceding widget in widg_parents
        # widg.widgetName
        current_widg = widg
        parents = str(widg).split('.')[-1:3:-1]
        found_test_name = ''
        found_unit_name = ''
        for widg_str in parents:
            if widg_str.startswith("!testframe"):
                found_test_name = current_widg.children['!label'].cget('text')
            if widg_str.startswith("!unitframe"):
                found_unit_name = current_widg.children['!label'].cget('text')
                break
            current_widg = current_widg.master
        else:
            print("no suitable parent frame found")
            return
        
        # print(f"Unit: '{found_unit_name}', Test: '{found_test_name}'")

        if found_unit_name:
            if found_test_name:
                return self.parent.project[found_unit_name][found_test_name]
            else:
                return self.parent.project[found_unit_name]
        else:
            # in case of a weird nesting, throw an error. This should not happen
            # in normal use
            print("no found unit name in ProjectView.get_clicked_test_or_unit()")
            raise RuntimeError("nesting depth issue in ProjectView.get_current_test_or_unit")

    def update_test_type(self, test):
        test.frame.children['!label2']['text'] = test.type

    def update_proj_header(self):
        self.proj_header.config(text=self.proj.title)
        print(self.parent.project.working_dir)
        self.proj_header_hover.text = "Working directory: " + self.proj.working_dir

    # @TODO make all of the dialogs custom
    # method used to delete a test
    # uses a messagebox to ask the user for confirmation
    def delete_test(self):
        test = self.get_clicked_test_or_unit()
        answer = messagebox.askyesno(
            message="Are you sure you want to delete the following test:\n\n"
                    + test.name,
            title="Delete Test"
        )
        if answer:
            if self.parent.focused_test == test:
                self.parent.focused_test = None
                self.parent.test_frame.show_focused_test()
                self.parent.param_frame.render()

            test.frame.destroy()
            test.parent.remove_test(test.name)
            if len(test.parent.tests) == 0:
                test.parent.no_tests_label.pack(anchor='w', padx=10)
            self.parent.set_status(
                f"Deleted test '{test.name}' in unit '{test.parent.name}'")

    # method used to rename a test
    # uses a dialog box to ask for the new test name
    def rename_test(self):
        test = self.get_clicked_test_or_unit()
        new_name = simpledialog.askstring(title="Rename Test",
            prompt="Enter a new name for the following test\n" + test.name)
        if not new_name:
            print("oopsie no new test name!")
        elif new_name in test.parent.tests:
            print(f"test {new_name} already exists. renaming test {test.name} failed")
        else:
            old_name = test.name
            test.parent.rename_test(test.name, new_name)
            test.frame.children['!label']['text'] = new_name
            self.parent.set_status(
                f"Renamed test '{old_name}' to '{test.name}' in unit '{test.parent.name}'.")

    def set_test_sub_dir(self):
        test = self.get_clicked_test_or_unit()
        
        set_dir_window = BaseOkPopup(self, title="Choose a new test sub-directory")
        
        dir_var = tk.StringVar(self, value=test.get_dir())
        
        def dir_select():
            dirname = fd.askdirectory(mustexist=True, initialdir=test.get_dir())
            if dirname:
                # @TODO add a printout of the number of paths that are valid from
                # choosing a new directory. maybe add a verify button?
                dir_var.set(dirname)
        
        def ok_command():
            sub_dir = dir_var.get()
            message_list = []
            
            if sub_dir:
                if sub_dir[-1] in '/\\':
                    sub_dir = sub_dir[:-1]
                
                if os.path.exists(sub_dir):
                    # if it's not a directory, complain
                    if not os.path.isdir(sub_dir):
                        message_list.append("The entered sub-directory is not a directory.")
                    else:
                        sub_dir = os.path.relpath(sub_dir, test.parent.get_dir()).replace('\\', '/')
                else:
                    message_list.append("The entered sub-directory does not exist.")
            else:
                message_list.append("Please enter a sub-directory for the test.")
        
            if message_list:
                # update the screen with errors
                set_dir_window.show_errors(message_list)
            else:
                set_dir_window.hide_errors()
            
                # close the new project window
                set_dir_window.destroy()
                
                if sub_dir != test.sub_dir:
                    test.sub_dir = sub_dir
                    # update hovertext
                    test.hovertext.text = "Sub Directory: " + test.sub_dir
                    if test == self.parent.focused_test:
                        # rerender focused test to update hovertext @TODO do it better
                        self.parent.test_frame.show_focused_test()
                self.parent.set_status(
                    f"Test '{test.name}' sub-directory changed to '{os.path.normpath(test.get_dir())}'.")
        
        def cancel_command():
            set_dir_window.destroy()
        
        dir_label = ttk.Label(set_dir_window.frame,
                text="Choose a new sub-directory. Ideally all necessary\n" \
                    + "simulation data (dyd, sav, csv, etc.) should be\n" \
                    + "somewhere in the sub-directory.")
        dir_label.grid(row=0, column=0, sticky='w', columnspan=2)
        
        dir_entry = ttk.Entry(set_dir_window.frame, textvariable=dir_var, width=45)
        dir_entry.grid(row=1, column=0)
        dir_entry.bind('<Return>', lambda e: ok_command())
        
        dir_select_button = ttk.Button(set_dir_window.frame, text="Choose Folder",
                                       command=dir_select)
        dir_select_button.grid(row=1, column=1, sticky='ew')
        dir_select_button.bind("<Return>", lambda e: dir_select())
        
        set_dir_window.wrapup(ok_command=ok_command, cancel_command=cancel_command)

    ## add test methods. all 3 are wrapper for the add_test method
    def add_test_from_test(self):
        test = self.get_clicked_test_or_unit()
        unit = test.parent
        self.add_test(unit)

    def add_test_from_unit(self):
        unit = self.get_clicked_test_or_unit()
        self.add_test(unit)

    def add_test_from_no_test(self):
        parent = self.clicked_widget.master
        unit_name = parent.children['!label'].cget('text')
        unit = self.proj[unit_name]
        self.add_test(unit)

    # add_test helper method. creates a custom top level window that asks the
    # user for a test name and type, as well as performing error checking
    # on their input and prompting them for fixes to those errors
    def add_test(self, unit):
        # double check that there's a working directory
        if not self.parent.validate_working_dir():
            return
        
        # create the add_test window
        test_prompt_window = BaseOkPopup(self.parent, "New Test")

        ## section for putting in single gui elements
        # add test name label
        name_label = ttk.Label(test_prompt_window.frame, text="Test Name")
        name_label.grid(row=0, column=0, padx=4, pady=4)

        # add test name entry
        name_var = tk.StringVar(test_prompt_window.frame)
        name_entry = ttk.Entry(test_prompt_window.frame, textvariable=name_var)
        name_entry.grid(row=0, column=1, padx=4, pady=4)
        # give the entry keyboard focus
        name_entry.focus_set()

        # add test type label
        type_label = ttk.Label(test_prompt_window.frame, text="Test Type")
        type_label.grid(row=1, column=0, padx=4, pady=4)

        # add test type interactible combobox (aka dropdown menu)
        type_var = tk.StringVar(test_prompt_window.frame)
        type_dropdown = ttk.Combobox(test_prompt_window.frame, textvariable=type_var)
        test_types = ("Voltage Reference", "Load Reference",
                      "Current Interruption", "Speed Reference",
                      "Steady State", "Synchronization")
        type_dropdown['values'] = test_types
        # state = readonly makes it so the user cannot add test types
        type_dropdown.state(['readonly'])
        type_dropdown.grid(row=1, column=1, padx=4, pady=4)

        dir_label = ttk.Label(test_prompt_window.frame,
            text="Choose an optional subdirectory for the\n" + \
                 "test's files to live in. Leave blank to skip.")
        dir_label.grid(row=2, column=0)
        
        def dir_button_command():
            dirname = fd.askdirectory(mustexist=True)
            if dirname:
                dir_var.set(dirname)
        
        dir_button = ttk.Button(test_prompt_window.frame, text="Select Subdirectory",
                                     command=dir_button_command)
        dir_button.grid(row=2, column=1)
        
        dir_var = tk.StringVar()
        dir_entry = ttk.Entry(test_prompt_window.frame, textvariable=dir_var, width=50)
        dir_entry.grid(row=3, column=0, columnspan=2)

        # function called by the create new test button, checks that the
        # name and test entered are valid and  if so creates a new test
        def ok_command():
            test_name = name_var.get()
            test_type = type_var.get()
            subdir = dir_var.get()
            message_list = []
            
            if test_name:
                # @TODO check for invalid characters, using validatecommand?
                if test_name in unit.tests:
                    message_list.append(f"Test \"{test_name}\" already exists")
            else:
                message_list.append("Please enter a test name")
            
            if test_type == '':
                message_list.append("Select a test type")

            if subdir:
                if subdir[-1] in '/\\':
                    subdir = subdir[:-1]
                
                if os.path.exists(subdir):
                    # if it's not a directory, complain
                    if not os.path.isdir(subdir):
                        message_list.append("The entered sub-directory is not a directory.")
                    else:
                        subdir = os.path.relpath(subdir, unit.get_dir()).replace('\\', '/')
                else:
                    message_list.append("The entered sub-directory does not exist.")
            

            if message_list:
                # update the screen with errors
                test_prompt_window.show_errors(message_list)
            else:
                test_prompt_window.hide_errors()
                
                test_prompt_window.destroy()
             
                ## add the test and update the projectview
                # if this is the first test we need to destroy the no tests label
                if len(unit.tests) == 0:
                    unit.no_tests_label.pack_forget()
                
                # add the test
                test = unit.add_test(test_name, test_type)
                # set the subdirectory
                if subdir == '.':
                    subdir = ''
                test.sub_dir = subdir
                # build the test frame and save it for later
                test_frame = self.build_test_frame(test, unit.frame)
                test.frame = test_frame
                
                self.parent.set_status(
                    f"Added test '{test.name}' to unit '{test.parent.name}'.")

        def cancel_command():
            test_prompt_window.destroy()


        # usability keybinds to make the combobox and button interface
        # more intuitive
        name_entry.bind("<Return>", lambda e: type_dropdown.focus())
        type_dropdown.bind("<Return>", lambda e: type_dropdown.event_generate('<Down>'))
        type_dropdown.bind("<space>", lambda e: type_dropdown.event_generate('<Down>'))
        type_dropdown.bind("<<ComboboxSelected>>", lambda e: dir_button.focus())
        
        test_prompt_window.wrapup(ok_command, cancel_command)

    ## @TODO make the unit methods use custom windows
    # delete the clicked unit
    def delete_unit(self):
        unit = self.get_clicked_test_or_unit()
        answer = messagebox.askyesno(
            message="Are you sure you want to delete the following unit and all of its tests:\n\n"
                    + unit.name,
            title="Delete Unit"
        )
        if answer:
            if self.parent.focused_test and self.parent.focused_test.name in unit.tests:
                self.parent.focused_test = None
                self.parent.test_frame.show_focused_test()
                self.parent.param_frame.render()
            
            unit.frame.destroy()
            unit.sep.destroy()
            self.proj.remove_unit(unit.name)
            if len(self.proj.units) == 0:
                self.show_no_units()
            self.parent.set_status(f"Deleted unit '{unit.name}'.")

    # rename the clicked unit
    # @TODO handle a cancel in the askstring popup
    # @TODO make sure that the entered string isn't empty
    def rename_unit(self):
        unit = self.get_clicked_test_or_unit()
        new_name = simpledialog.askstring(title="Rename Unit",
            prompt="Enter a new name for the following unit\n" + unit.name)
        if not new_name:
            print("no text entered for new unit name! oopsie!")
        elif new_name in self.proj.units:
            print(f"unit {new_name} already exists. renaming unit {unit.name} failed")
        else:
            old_name = unit.name
            self.proj.rename_unit(unit.name, new_name)
            unit.frame.children['!label']['text'] = new_name
            self.parent.set_status(f"Renamed unit '{old_name}' to '{unit.name}'.")

    def set_unit_sub_dir(self):
        unit = self.get_clicked_test_or_unit()
        
        set_dir_window = BaseOkPopup(self, title="Choose a new unit sub-directory")
        
        dir_var = tk.StringVar(self, value=unit.get_dir())
        
        def dir_select():
            dirname = fd.askdirectory(mustexist=True, initialdir=unit.get_dir())
            if dirname:
                # @TODO add a printout of the number of paths that are valid from
                # choosing a new directory. maybe add a verify button?
                dir_var.set(dirname)
        
        def ok_command():
            sub_dir = dir_var.get()
            message_list = []
            
            if sub_dir:
                if sub_dir[-1] in '/\\':
                    sub_dir = sub_dir[:-1]
                
                if os.path.exists(sub_dir):
                    # if it's not a directory, complain
                    if not os.path.isdir(sub_dir):
                        message_list.append("The entered sub-directory is not a directory.")
                    else:
                        sub_dir = os.path.relpath(sub_dir, unit.parent.get_dir()).replace('\\', '/')
                else:
                    message_list.append("The entered sub-directory does not exist.")
            else:
                message_list.append("Please enter a sub-directory for the unit.")
        
            if message_list:
                # update the screen with errors
                set_dir_window.show_errors(message_list)
            else:
                set_dir_window.hide_errors()
            
                # close the new project window
                set_dir_window.destroy()
                
                if sub_dir != unit.sub_dir:
                    unit.sub_dir = sub_dir
                    # update hovertext
                    unit.hovertext.text = "Sub Directory: " + unit.sub_dir
                    if self.parent.focused_test.name in unit.tests:
                        # rerender focused test to update hovertext @TODO do it better
                        self.parent.test_frame.show_focused_test()
                
                self.parent.set_status(
                    f"Unit '{unit.name}' sub-directory changed to '{os.path.normpath(unit.get_dir())}'.")
        
        def cancel_command():
            set_dir_window.destroy()
        
        dir_label = ttk.Label(set_dir_window.frame,
                text="Choose a new sub-directory. Ideally all necessary\n" \
                    + "simulation data files (dyd, sav, csv, etc.) should be\n" \
                    + "somewhere in the sub-directory or below it.")
        dir_label.grid(row=0, column=0, sticky='w', columnspan=2)
        
        dir_entry = ttk.Entry(set_dir_window.frame, textvariable=dir_var, width=45)
        dir_entry.grid(row=1, column=0)
        dir_entry.bind('<Return>', lambda e: ok_command())
        
        dir_select_button = ttk.Button(set_dir_window.frame, text="Choose Folder",
                                       command=dir_select)
        dir_select_button.grid(row=1, column=1, sticky='ew')
        dir_select_button.bind("<Return>", lambda e: dir_select())
        
        set_dir_window.wrapup(ok_command=ok_command, cancel_command=cancel_command)


    # add a unit to the project structure
    def add_unit(self):
        # double check that there's a working directory
        if not self.parent.validate_working_dir():
            return
        
        unit_prompt_window = BaseOkPopup(self.parent, "New Unit")
        
        name_label = ttk.Label(unit_prompt_window.frame, text="Enter a name for the Unit:")
        name_label.grid(row=0, column=0)
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(unit_prompt_window.frame, textvariable=name_var)
        name_entry.grid(row=0, column=1)
        name_entry.focus_set()
        
        dir_label = ttk.Label(unit_prompt_window.frame,
            text="Choose an optional subdirectory for the\n" + \
                 "unit's files to live in. Leave blank to skip.")
        dir_label.grid(row=1, column=0)
        
        def dir_button_command(e=None):
            dirname = fd.askdirectory(mustexist=True)
            if dirname:
                dir_var.set(dirname)
        
        dir_button = ttk.Button(unit_prompt_window.frame, text="Select Subdirectory",
                                     command=dir_button_command)
        dir_button.grid(row=1, column=1)
        
        dir_var = tk.StringVar()
        dir_entry = ttk.Entry(unit_prompt_window.frame, textvariable=dir_var, width=50)
        dir_entry.grid(row=2, column=0, columnspan=2)
        
        def ok_command(e=None):
            unit_name = name_var.get()
            subdir = dir_var.get()
            message_list = []
            
            if unit_name:
                if unit_name in self.proj.units:
                    message_list.append("A unit with this name already exists.")
                # check for weird characters?
            else:
                message_list.append("Please enter a name for the unit.")
            
            if subdir:
                if subdir[-1] in '/\\':
                    subdir = subdir[:-1]
                
                if os.path.exists(subdir):
                    # if it's not a directory, complain
                    if not os.path.isdir(subdir):
                        message_list.append("The entered sub-directory is not a directory.")
                    else:
                        subdir = os.path.relpath(subdir, self.parent.project.working_dir).replace('\\', '/')
                else:
                    message_list.append("The entered sub-directory does not exist.")
            
            if message_list:
                # update the screen with errors
                unit_prompt_window.show_errors(message_list)
            else:
                unit_prompt_window.hide_errors()
                
                unit_prompt_window.destroy()
                
                if len(self.proj.units) == 0:
                    self.no_unit_label.destroy()
                    self.no_unit_sep.destroy()
                unit = self.proj.add_unit(unit_name)
                
                if subdir == '.':
                    subdir = ''
                unit.sub_dir = subdir

                unit_frame = self.build_unit_frame(unit, self.scroller.frame)
                unit.frame = unit_frame
                
                self.parent.set_status(
                    f"Created unit '{unit.name}'.")
        
        def cancel_command(e=None):
            unit_prompt_window.destroy()

        dir_button.bind("<Return>", dir_button_command)
        name_entry.bind("<Return>", lambda e: dir_button.focus())
        
        unit_prompt_window.wrapup(ok_command, cancel_command)


    # helper method to set the root's focused test to the clicked widget
    def focus_test(self, event):
        temp_test = self.get_clicked_test_or_unit(event.widget)
        if temp_test != self.parent.focused_test:
            # unset frame on old test
            if self.parent.focused_test:
                self.parent.focused_test.frame.config(relief='flat')
            temp_test.frame.config(relief='groove')
            # set frame on new test
            self.parent.focused_test = temp_test
            self.parent.test_frame.show_focused_test()
            self.parent.param_frame.render()
