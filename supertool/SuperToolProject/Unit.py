# Unit.py, Charlie Jordan, 1/22/2024
# Unit class for the super tool gui. Used to
# contain tests


from supertool.SuperToolProject.Test import Test

# class containing a unit, its information, and its tests
class Unit:
    def __init__(self, parent, name="Untitled Unit"):
        self.name = name
        self.tests: dict[str,Test] = {}
        self.sub_dir = ''
        # @TODO put more unit specific info here
        
        self.parent = parent
        
        self.frame = None
        self.sep = None
        self.no_tests_label = None
        self.hovertext = None
        
    # add a test to this unit given a name and type
    def add_test(self, name, type_):
        self.tests[name] = Test(name=name, type_=type_)
        self.tests[name].parent = self
        return self.tests[name]
    
    # rename a test in the test dictionary and update it's location
    def rename_test(self, old, new):
        self.tests[new] = self.tests.pop(old)
        self.tests[new].name = new
        
    # remove a test from the dictionary
    def remove_test(self, name):
        del self.tests[name]
    
    def get_dir(self):
        if self.sub_dir:
            end = self.sub_dir + '/'
        else:
            end = ''
        return self.parent.get_dir() + end
    
    # overload string conversion
    def __str__(self):
        return "  [U {}]".format(self.name) + \
            "".join(["\n" + str(i) for i in self.tests.values()]) 
    
    # allow indexing of the test dictionary
    # setitem and delitem are not included (yet)
    def __getitem__(self, key):
        return self.tests[key]
        
    # DEPRECATED
    # internal write method to write a unit and its tests to a file
    def write(self, file):
        """Deprecated project save method. Use write_to_file_name instead."""
        file.write("\t".join(
            ["U", self.name]
            ) + "\n")
        for test in self.tests.values():
            test.write(file)
    
    # DEPRECATED
    # internal read method to read a unit and its tests from the lines of a file
    def read(self, lines):
        """Deprecated project save method. Use read_from_file_name instead."""
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
    