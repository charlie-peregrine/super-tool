# Unit.py, Charlie Jordan, 1/22/2024
# Unit class for the super tool gui. Used to
# contain tests


from supertool.SuperToolProject.Test import Test

# class containing a unit, its information, and its tests
class Unit:
    def __init__(self, name="Untitled Unit"):
        self.name = name
        self.tests = {}
        # @TODO put more unit specific info here
        
    # add a test to this unit given a name and type
    def add_test(self, name, type_):
        self.tests[name] = Test(name=name, type=type_)
        self.tests[name].parent = self
    
    # rename a test in the test dictionary and update it's location
    def rename_test(self, old, new):
        self.tests[new] = self.tests.pop(old)
        self.tests[new].name = new
        
    # remove a test from the dictionary
    def remove_test(self, name):
        del self.tests[name]
    
    # internal write method to write a unit and its tests to a file
    def write(self, file):
        file.write("\t".join(
            ["U", self.name]
            ) + "\n")
        for test in self.tests.values():
            test.write(file)
    
    # internal read method to read a unit and its tests from the lines of a file
    def read(self, lines):
        line = lines.pop()
        print('u', line)
        
        # if there are no more lines to read end the command
        if line == '':
            return False, lines
        
        if line[0] == "U":
            _, self.name = line.split("\t")
        else:
            raise ValueError("not a unit")
        
        while lines:
            t, lines = Test().read(lines)
            if not t:
                break
            t.parent = self
            self.tests[t.name] = t
        
        return self, lines
    
    # overload string conversion
    def __str__(self):
        return "  [U {}]".format(self.name) + \
            "".join(["\n" + str(i) for i in self.tests.values()]) 
    
    # allow indexing of the test dictionary
    # setitem and delitem are not included (yet)
    def __getitem__(self, key):
        return self.tests[key]
        
