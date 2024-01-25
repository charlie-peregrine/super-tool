# Project.py, Charlie Jordan, 11/17/2023
# file containing the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data

import tkinter as tk
import xml.etree.ElementTree as ET

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
    
    def write_to_file_name(self, *args):
        print("building xml ElementTree for writing")
        tree = ET.ElementTree(
            ET.Element("project", 
                       {"title": self.title}))
        root = tree.getroot()
        for unit_name, unit in self.units.items():
            unit_node = ET.Element("unit", {"name": unit_name})
            for test_name, test in unit.tests.items():
                test_node = ET.Element("test", 
                                       {"name": test_name,
                                        "type": test.type})
                for attr_name, attr in test.attrs.items():
                    attr_node = ET.Element("attr",
                                           {"name": attr_name})
                    attr_node.text = str(attr.var.get())
                    test_node.append(attr_node)
                    print(unit_name, test_name, attr_name, attr.var.get())
                
                header_loop_data = (("sim", test.sim_headers),
                                    ("mes", test.mes_headers))
                for header_type, header_dict in header_loop_data:
                    for key, (header, expr) in header_dict.items():
                        header_node = ET.Element("chnl", 
                                                {"type": header_type,
                                                 "name": key,
                                                 "expr": expr.get()})
                        header_node.text = header.get()
                        
                        test_node.append(header_node)
                    
                unit_node.append(test_node)
            root.append(unit_node)
        
        ET.indent(tree, space="    ", level=0)
        tree.write(self.file_name, short_empty_elements=False)
    
    # deprecated
    # wrapper for write, intended for use by the gui
    # does not check if the file_name is valid
    def __write_to_file_name(self, *args):
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
    
    def read_from_file_name(self):
        # backwards compatibility for old format
        with open(self.file_name, 'r') as file:
            line = file.readline()
            if line[0] == 'P' and line[1] in '\t ':
                print(f"reading {self.file_name} as an old format .pec file")
                self.__read_from_file_name()
                return
        
        print(f"reading {self.file_name} as an xml format .pec file")
        tree = ET.parse(self.file_name)
        root = tree.getroot()
        
        del self.units
        self.units = {}
        
        def none_to_str(v):
            if v == None:
                return ''
            return v
        
        # KeyError for dict keys   v
        self.title = root.attrib['title']
        for unit_node in root:
            unit = Unit(unit_node.attrib['name'])
            for test_node in unit_node:
                test = Test(name=test_node.attrib['name'],
                            type=test_node.attrib['type'],
                            parent=unit)
                for attr_node in test_node:
                    # print(unit_node.attrib, test_node.attrib, attr_node.attrib, attr_node.text)
                    
                    if attr_node.tag == 'attr':
                        val = none_to_str(attr_node.text)
                        test.add_attr(attr_node.attrib['name'], val)
                    
                    elif attr_node.tag == 'chnl': 
                        header_type = attr_node.attrib['type']
                        header_key = attr_node.attrib['name']
                        header_pair = [none_to_str(attr_node.text), attr_node.attrib['expr']]
                        header_pair = [tk.StringVar(value=s) for s in header_pair]
                        if header_type == 'sim':
                            test.sim_headers[header_key] = header_pair
                        elif header_type == 'mes':
                            test.mes_headers[header_key] = header_pair

                unit.tests[test.name] = test
            self.units[unit.name] = unit
    
    # deprecated
    # wrapper for read method, intended for use by the gui
    # resets the dictionary of units and starts reading from the lines
    # of the file
    def __read_from_file_name(self):
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
