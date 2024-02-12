# Attribute.py, Charlie Jordan, 1/22/2024
# houses the attribute class, which stores information
# for tests

import tkinter as tk

# attribute class that stores details like name, type, the measuring units,
# and a tk variable that updates with the gui
class Attribute:
    def __init__(self, name: str, defaults: dict):
        self.name = name
        self.type = defaults['type']
        
        if self.type == 'PATH':
            self.var = tk.StringVar(value=defaults['default'])
            self.read_only_file = defaults['read_only']
            self.extension = defaults['extension']
        elif self.type == 'BOOL':
            self.var = tk.BooleanVar(value=defaults['default'])
        elif self.type == 'NUM':
            self.var = tk.DoubleVar(value=defaults['default'])
            self.unit = defaults['unit']
        else:
            raise ValueError(f"Attribute type {self.type} is not valid")
    
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
    