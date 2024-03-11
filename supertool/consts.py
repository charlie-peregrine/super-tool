# consts.py, Charlie Jordan, 1/23/2024
# loads constants from config.json

import json
import os
import inspect
from tkinter.messagebox import showwarning
from supertool.Version import Version

# save the directory that the source code is run from
filename = inspect.getframeinfo(inspect.currentframe()).filename # type: ignore
SUPERTOOL_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(filename)), '..'))

os.chdir(SUPERTOOL_DIR)

print("===== File Constants =====")
print("SuperTool Folder:", SUPERTOOL_DIR)
print("Config file     :", os.path.join(SUPERTOOL_DIR, 'config.json'))

print("===== loading config.json =====")
try:
    config_data = json.load(open('config.json', 'r', encoding='utf-8'))
except FileNotFoundError:
    showwarning(title="Un-configured Installation",
        message="No Configuration file created yet. Please run setup.py first.")
    exit()

VEUSZ_PATH = config_data['VEUSZ_PATH']
# backwards compatibility
if 'HIDE_PSLF_GUI' not in config_data:
    config_data['HIDE_PSLF_GUI'] = True
HIDE_PSLF_GUI = config_data['HIDE_PSLF_GUI']
MY_ENV = os.environ.copy()
MY_ENV["PATH"] += VEUSZ_PATH + ';'

print("===== config.json loaded =====")

# application wide hover delay
HOVER_DELAY = 300

# current version, v1.4.4 -> (1,4,4)
VERSION = Version(1,4,5)
GITHUB_REPO = "https://github.com/charlie-peregrine/super-tool/releases/latest"

print("===== loading default_test_attributes.json =====")

with open("default_test_attributes.json", 'r', encoding='utf-8') as file:
    DEFAULT_TEST_ATTRIBUTES = json.load(file)

print("===== default_test_attributes.json loaded =====")
