# consts.py, Charlie Jordan, 1/23/2024
# loads constants from config.json

import json
import os
from tkinter.messagebox import showwarning


print("===== loading config.json =====")
try:
    config_data = json.load(open('config.json', 'r'))
except FileNotFoundError:
    showwarning(title="Un-configured Installation",
        message="No Configuration file created yet. Please run config.py first.")
    exit()

VEUSZ_PATH = config_data['VEUSZ_PATH']
HIDE_PSLF_GUI = config_data['HIDE_PSLF_GUI']
MY_ENV = os.environ.copy()
MY_ENV["PATH"] += VEUSZ_PATH + ';'

print("===== config.json loaded =====")