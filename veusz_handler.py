# veusz_handler.py, Charlie Jordan, 1/5/2023
# handles the veusz program calls and passing the right files
# to veusz. Also modifies the fvsz (vsz files with python format
# blocks in them) to use the right headers and csv files


# # importing veusz using importlib.util, not currently in use
# try:
#     import veusz.embed as veusz
#     print(veusz)
#     print("import worked normally")

# except:
#     import importlib.util
#     import sys

#     spec = importlib.util.spec_from_file_location("veusz.embed",
#             VEUSZ_PATH + "embed.py")
#     veusz = importlib.util.module_from_spec(spec)
#     sys.modules["veusz.embed"] = veusz
#     spec.loader.exec_module(veusz)
    
#     print(veusz)
#     print("importlib.util worked")

VEUSZ_PATH = "C:/Program Files (x86)/Veusz/"
# @TODO add veusz_path to user path, prolly done in an install script

import time

import subprocess
import re

# mes_file_name = 'C:/Users/charlie/Downloads/SampleProject/SampleFolder/Voltage_Reference.csv'
# sim_file_name = 'C:/Users/charlie/Downloads/SampleProject/SampleFolder/Voltage_Reference_sim.csv'

def plot_voltage_reference(sim_file='', mes_file=''):
    with open("veusz_files/Voltage_Reference.fvsz", 'r') as file:
        text_to_format = file.read()


    if sim_file and mes_file:
        # leave time as x or dependent variable as y to blank it
        result_text = text_to_format.format(s_filename=sim_file,
                            s_time='Time',
                            s_vt='"vt   1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            s_p='"pg   1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            s_q='"qg   1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            s_efd='"efd  1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            s_ifd='"ifd  1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            m_filename=mes_file,
                            m_time='Seconds',
                            m_vt='Vave 0',
                            m_p='KW 0',
                            m_q='Kvar 0',
                            m_efd='Vfd 0',
                            m_ifd='Ifd 0'
                            )
    elif sim_file:
        pattern = r"Add\('xy', name='Measured'(?:.*\n)+?To\('\.\.'\)\n|.*{m_filename}.*\n"
        text_to_format = re.sub(pattern, '', text_to_format, flags=re.MULTILINE)
        
        result_text = text_to_format.format(s_filename=sim_file,
                            s_time='Time',
                            s_vt='"vt   1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            s_p='"pg   1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            s_q='"qg   1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            s_efd='"efd  1"GENERATOR   "-0 "            " [1 ] [1 ]  "',
                            s_ifd='"ifd  1"GENERATOR   "-0 "            " [1 ] [1 ]  "'
                            )
    elif mes_file:
        pattern = r"Add\('xy', name='Simulated'(?:.*\n)+?To\('\.\.'\)\n|.*{s_filename}.*\n"
        text_to_format = re.sub(pattern, '', text_to_format, flags=re.MULTILINE)
        
        result_text = text_to_format.format(m_filename=mes_file,
                            m_time='Seconds',
                            m_vt='Vave 0',
                            m_p='KW 0',
                            m_q='Kvar 0',
                            m_efd='Vfd 0',
                            m_ifd='Ifd 0'
                            )
    else:
        result_text = ''
        print("uh oh no file names")
        

    if result_text:
        # @TODO make the filename unique enough
        with open("veusz_files/.blahg.vsz", 'w') as file:
            file.write(result_text)

        process = subprocess.Popen('"' + VEUSZ_PATH + 'veusz.exe" ./veusz_files/.blahg.vsz') #, shell=True)
        
        return process
        
        # process.kill()

