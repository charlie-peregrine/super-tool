# SuperToolProject.py, Charlie Jordan, 11/17/2023
# file containing all the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data

import pprint

class Project:
    def __init__(self, filename=''):
        self.title = "Untitled Project"
        self.file_name = "default-project.pec"
        self.unit_dict = {}
    
    def write_to_file(self, *args):
        with open(self.file_name, mode='w') as file:
            file.write("\t".join(
                ["P", self.title,
                 self.file_name]
                ) + "\n")
            
            for unit in self.unit_dict:
                file.write("\t".join(
                    ["U", unit.name]
                    ) + "\n")
                for test in unit.test_list:
                    file.write("\t".join([
                        "T", str(test.number), test.type]
                        ) + "\n")
                    # for k,v in test.attribute_dict:
                    #     write(k + "\t" + v)
            
    
    def read_from_file(self):
        pass

class Unit:
    def __init__(self):
        self.name = "Untitled Unit"
        self.test_dict = {}
    
    def add_test(self, number=-1, type="None", **kwargs):
        new_test = Test(number, type, **kwargs)
        self.test_dict[number] = new_test
        
class Test:
    # @TODO handle kwargs
    def __init__(self, number=-1, type="None", **kwargs):
        self.number = number
        self.type = type
        self.attribute_dict = {}
