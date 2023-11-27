# SuperToolProject.py, Charlie Jordan, 11/17/2023
# file containing all the class information for the background
# Super Tool Project. Handles reading and writing to save
# files and storing test, unit, and plot data

class Project:
    def __init__(self, filename=''):
        self.title = "Untitled Project"
        self.file_name = "default-project.pec"
        self.units = {}
    
    def write_to_file(self, *args):
        with open(self.file_name, mode='w') as file:
            file.write("\t".join(
                ["P", self.title,
                 self.file_name]
                ) + "\n")
            
            for unit in self.units.values():
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

    def add_unit(self, name):
        self.units[name] = Unit(name)

    # @TODO add error checking above this call?
    def rename_unit(self, old, new):
        self.units[new] = self.units.pop(old)
        self.units[new].name = new

    def remove_unit(self, name):
        del self.units[name]

    def __str__(self):
        return "[{} | {}]".format(self.title, self.file_name) + \
            "".join(["\n" + str(i) for i in self.units.values()])
    
    def __getitem__(self, key):
        return self.units[key]
    

class Unit:
    def __init__(self, name="Untitled Unit"):
        self.name = name
        self.tests = {}
        
    def add_test(self, name, type_):
        self.tests[name] = Test(name=name, type=type_)
    
    def rename_test(self, old, new):
        self.tests[new] = self.tests.pop(old)
        self.tests[new].name = new
        
    def remove_test(self, name):
        del self.tests[name]
    
    def __str__(self):
        return "  [{}]".format(self.name) + \
            "".join(["\n" + str(i) for i in self.tests.values()]) 
    
    def __getitem__(self, key):
        return self.tests[key]
        
class Test:
    # @TODO handle kwargs
    def __init__(self, name="Untitled Test", type="None", **kwargs):
        self.name = name
        self.type = type
        self.attribute_dict = kwargs
    
    def __str__(self):
        return "    [ {} | {} | {} ]".format(self.name, self.type, self.attribute_dict)
