# Attribute.py, Charlie Jordan, 1/22/2024
# houses the attribute class, which stores information
# for tests

import os
import tkinter as tk

# attribute class that stores details like name, type, the measuring units,
# and a tk variable that updates with the gui
class Attribute:
    def __init__(self, parent, name: str, defaults: dict):
        self.name = name
        self.type = defaults['type']
        self.group = defaults['group']
        
        self.parent = parent

        if self.type == 'PATH':
            self.var = tk.StringVar(value=defaults['default'])
            self.read_only_file = defaults['read_only']
            self.extension = defaults['extension']
        elif self.type == 'BOOL':
            self.var = tk.BooleanVar(value=defaults['default'])
        elif self.type == 'NUM':
            self.var = tk.DoubleVar(value=defaults['default'])
            self.unit = defaults['unit']
        elif self.type == 'STR':
            self.var = tk.StringVar(value=defaults['default'])
        else:
            raise ValueError(f"Attribute type {self.type} is not valid")
        
        self.full_name = defaults['full_name']
        self.description = defaults['description']
    
    def get(self):
        if self.type == 'PATH':
            return os.path.normpath(self.parent.get_dir() + self.var.get())
        elif self.type == 'BOOL':
            return self.var.get()
        elif self.type == 'NUM':
            return self.var.get()
        elif self.type == 'STR':
            return self.var.get()
        else:
            raise ValueError(f"Invalid attribute type for get: {self.type}")
    
    # string conversion overload
    def __str__(self):
        return "      [A {} | {} | {} ]".format(
            self.name, self.type, self.var.get()
        )
    
    # DEPRECATED
    def write(self, file):
        """Deprecated project save method. Use write_to_file_name instead."""
        file.write("\t".join([
                "A", self.name, str(self.var.get())
        ]) + "\n")
    
    # DEPRECATED
    @staticmethod
    def read(lines):
        """Deprecated project save method. Use read_from_file_name instead."""
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
