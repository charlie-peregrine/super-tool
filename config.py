# config.py


import json

if __name__ == '__main__':
    from tkinter.filedialog import askdirectory
    dir = askdirectory(title="Select the directory containing veusz.exe")
    json.dump({"VEUSZ_PATH" : dir}, open('config.json', 'w'), indent=4)

try:
    config_data = json.load(open('config.json', 'r'))
except FileNotFoundError:
    print("No Configuration file created yet. Please run config.py first.")
    exit()

VEUSZ_PATH = config_data['VEUSZ_PATH']