# test.py, Charlie Jordan, 11/21/2023
# a python program to test SuperToolProject.py from
# the terminal  without a gui

import SuperToolProject as stp

def main():
    # p1 = stp.Project()
    # u1 = stp.Unit()
    # t1 = stp.Test()
    # print(p1)
    # print(u1)
    # print(t1)
    
    # t1.name = "brop"
    # p1.unit_list.append(u1)
    # p1.unit_list.append(u1)
    # u1.test_list.append(t1)
    # u1.test_list.append(stp.Test(name="frogge"))

    # print(p1)

    import tkinter as tk
    root = tk.Tk()
    p = stp.Project()
    p.file_name = "blag.pec"
    p.read_from_file_name()
    while True:
        print("=========================================")
        print("1: add unit 2: rename unit 3: delete unit")
        print("4: add test 5: rename test 6: delete test")
        print("7: quit")
        print(p)
        print("=========================================")
        choice = int(input())
        
        match choice:
            case 1:
                name = input("unit name: ")
                p.add_unit(name)
            case 2:
                old = input("old name: ")
                new = input("new name: ")
                p.rename_unit(old, new)
            case 3:
                name = input("unit name: ")
                p.remove_unit(name)
            case 4:
                unit_name = input("which unit: ")
                name = input("name: ")
                type_ = input("type: ")
                p[unit_name].add_test(name, type_)
            case 5:
                unit_name = input("which unit: ")
                old = input("old name: ")
                new = input("new name: ")
                p[unit_name].rename_test(old, new)
            case 6:
                unit_name = input("which unit: ")
                name = input("test name: ")
                p[unit_name].remove_test(name)
            case 7:
                break


if __name__ == '__main__':
    main()