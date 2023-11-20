# SuperToolProject.py, Charlie Jordan, 11/17/2023
# file containing all the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data


class Project:
    def __init__(self, filename=''):
        self.title = "Untitled Project"
        self.file_name = "default-project.sprtl"
        self.unit_list = []
    
    def write_to_file(self):
        pass
    
    def read_from_file(self):
        pass

class Unit:
    def __init__(self):
        self.name = "Untitled Unit"
        self.test_list = []
        
class Test:
    def __init__(self):
        self.number = -1
        self.type = "default type"
        self.attribute_list = []
