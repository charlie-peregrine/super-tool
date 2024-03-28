# supertooltools.py, Charlie Jordan, 3/27/2024
# wrappers for add on tools for the supertool gui

import sys
import os.path
import subprocess
import supertool.consts as consts

TOOLS_DIR = os.path.join(consts.SUPERTOOL_DIR, 'tools')
print(TOOLS_DIR)

def run_csv_time_convert():
    return subprocess.Popen([
        sys.executable,
        os.path.join(TOOLS_DIR, 'CSV_Time_Convert_Tool.py')
        ]
    )
