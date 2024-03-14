
try:
    print("===== Printing Python Info =====")
    import sys
    import os.path
    import inspect
    
    filename = inspect.getframeinfo(inspect.currentframe()).filename # type: ignore
    path = os.path.dirname(os.path.abspath(filename))
    print("Python Version:", sys.version)
    print("Executable:    ", sys.executable)
    print("Working dir:   ", path)
    print("Running File:  ", filename)
    print("Arguments:     ", " ".join(sys.argv))
    print("Command:       ", f'"{sys.executable}" "{filename}"{" " + " ".join(sys.argv[1:])}')

    print("===== Initializing SuperTool =====")
    import supertool.SuperToolGUI as stgui

    print("===== Starting Supertool =====")
    gui = stgui.SuperToolGUI()
    gui.mainloop()

except Exception as e:
    print("########### ERROR ###########\n")
    import traceback
    traceback.print_exception(e)
    print("\n######### END ERROR #########\n")
    input("\nPress Enter to close")
    