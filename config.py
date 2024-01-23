# config.py


import json
import os
from tkinter.messagebox import showwarning, showinfo

if __name__ == '__main__':
    from tkinter.filedialog import askopenfilename
    import subprocess
    import time
    
    try:
        import win32
    except ModuleNotFoundError:
        print("===== Installing pywin32 =====")
        subprocess.call("python -m pip install pywin32")
        print("===== pywin32 Installed!")
    
    print("===== Finding veusz =====")
    try:
        where_output = subprocess.check_output("where veusz").decode('utf-8').strip()
    except subprocess.CalledProcessError:
        where_output = ''
    
    dir = ''
    if where_output:
        print("===== Veusz Found!")
        if '\n' in where_output:
            where_output = where_output.split('\n')[0]
        dir = askopenfilename(
                title="Find and select veusz.exe on your computer",
                initialdir=os.path.dirname(where_output),
                filetypes=[("Executable", "*.exe"),
                           ("All Files", "*.*")]
                )
        dir = os.path.dirname(dir)
    else:
        print("===== Veusz Not Found")
        dir = askopenfilename(
                title="Find and select veusz.exe on your computer",
                filetypes=[("Executable", "*.exe"),
                           ("All Files", "*.*")]
                )
        dir = os.path.dirname(dir)

    # print("===== Finding Veusz on PATH =====")
    # user_path = subprocess.check_output("echo %PATH%", shell=True).decode('utf-8')
    # win_dir = dir.replace('/','\\')
    # if win_dir not in user_path:
    #     print("===== Veusz not found on PATH. Prompt user.")
    #     showinfo(title="Add to path",
    #                 message=f"On the next window please add\n{dir}\nto your user or system path variable.")
    #     print(win_dir)
    #     subprocess.call(r"C:\WINDOWS\system32\rundll32.exe sysdm.cpl,EditEnvironmentVariables", shell=True)
    # else:
    #     print("===== Veusz found on PATH!")
        
    
    json.dump({"VEUSZ_PATH" : dir}, open('config.json', 'w'), indent=4)
    print("Configuration Saved!")
    showinfo(title="Configuration complete",
             message="Configuration complete!\nClick Ok to finish.")
    

print("===== loading config.json =====")
try:
    config_data = json.load(open('config.json', 'r'))
except FileNotFoundError:
    showwarning(title="Un-configured Installation",
        message="No Configuration file created yet. Please run config.py first.")
    exit()

VEUSZ_PATH = config_data['VEUSZ_PATH']
MY_ENV = os.environ.copy()
MY_ENV["PATH"] += VEUSZ_PATH + ';'

print("===== config.json loaded =====")