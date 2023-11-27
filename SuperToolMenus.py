# SuperToolMenus.py, Charlie Jordan, 11/27/2023
# a collection of menus for the various interface elements
# of the SuperTool windows

import tkinter as tk
from tkinter import ttk
from superbackend import *
from SuperToolFrames import *
import SuperToolProject as stp

class UnitLabel(ttk.Label):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(self.parent, **kwargs)
        
        self.menu = ProjectUnitMenu(self)
        self.bind('<3>', lambda e: self.menu.post(e.x_root, e.y_root))

class TestLabel(ttk.Label):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(self.parent, **kwargs)
        
        self.menu = ProjectTestMenu(self)
        self.bind('<3>', lambda e: self.menu.post(e.x_root, e.y_root))


class ProjectUnitMenu(tk.Menu):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(self.parent)
        
        self.add_command(label="Rename Unit")
        self.add_command(label="Delete Unit")
        self.add_command(label="Add Test")

class ProjectTestMenu(tk.Menu):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(self.parent)
        
        self.add_command(label="Rename Test")
        self.add_command(label="Delete Test")