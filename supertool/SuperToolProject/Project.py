# Project.py, Charlie Jordan, 11/17/2023
# file containing the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data

from supertool.SuperToolProject.Unit import Unit
from supertool.SuperToolProject.Test import Test
from supertool.SuperToolProject.Attribute import Attribute

# main class that holds information of units and tests
# contains title and filename of the project, as well as 
# a dictionary of the units it holds
class Project:
    def __init__(self, title="Untitled Project", filename=''):
        self.title = title
        self.file_name = ''
        self.units = {}
    
    # wrapper for write, intended for use by the gui
    # does not check if the file_name is valid
    def write_to_file_name(self, *args):
        with open(self.file_name, mode='w') as file:
            self.write(file)
            
    # internal write method, writes the project section to a file
    # and then delegates to each unit to write its details, effectively
    # recursing through the project tree
    def write(self, file):
        file.write("\t".join(
            ["P", self.title]
            ) + "\n")
        for unit in self.units.values():
            unit.write(file)
    
    # wrapper for read method, intended for use by the gui
    # resets the dictionary of units and starts reading from the lines
    # of the file
    def read_from_file_name(self):
        with open(self.file_name, mode='r') as file:
            lines = file.read().split('\n')[::-1]

        del self.units
        self.units = {}
        
        self.read(lines)

    # internal method for reading the project from lines of a file
    # and then passing control to units to read those
    def read(self, lines):
        line = lines.pop()
        print('p', line)
        if line[0] == "P":
            self.title = line.split("\t")[1]
        else:
            raise ValueError("not a project")
        print(self)
        
        while lines:
            u, lines = Unit().read(lines)
            if not u:
                break
            self.units[u.name] = u

    # add a unit to the unit dictionary
    def add_unit(self, name):
        self.units[name] = Unit(name)

    # rename a unit and update it's location in the unit dictionary
    # @TODO add error checking above this call?
    def rename_unit(self, old, new):
        self.units[new] = self.units.pop(old)
        self.units[new].name = new

    # delete a unit and delete it's tests too
    # @TODO check to see if making a custom clearing command that works
    # down through the tree is necessary
    def remove_unit(self, name):
        del self.units[name].tests
        del self.units[name]

    # printout for the project and all of its subsections
    # overloads str(project) and print(project)
    def __str__(self):
        return "[P {} | {}]".format(self.title, self.file_name) + \
            "".join(["\n" + str(i) for i in self.units.values()])
    
    def __getitem__(self, key):
        return self.units[key]

