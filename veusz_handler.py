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

    # get column titles for the simulated data
    sim_dict = {}
    if sim_file:
        with open(sim_file, 'r') as file:
            headers = file.readline().replace(',', '\n')
        sim_dict['time'] = re.findall(r'.*time.*', headers, flags=re.IGNORECASE)
        sim_dict['vt'] = re.findall(r'"vt\s+1"?gen.*', headers, flags=re.IGNORECASE)
        sim_dict['pg'] = re.findall(r'"pg\s+1"?gen.*', headers, flags=re.IGNORECASE)
        sim_dict['qg'] = re.findall(r'"qg\s+1"?gen.*', headers, flags=re.IGNORECASE)
        sim_dict['efd'] = re.findall(r'"efd\s+1"?gen.*', headers, flags=re.IGNORECASE)
        sim_dict['ifd'] = re.findall(r'"ifd\s+1"?gen.*', headers, flags=re.IGNORECASE)

        for k,v in sim_dict.items():
            print(len(sim_dict[k]), sim_dict[k])
            if len(sim_dict[k]) == 0:
                print(f"blah blah {k} has zero oops")
                sim_dict[k] = 'x'
            else:
                if len(sim_dict[k]) > 1:
                    print(f"blah blah {k} too many, picking the first one")
                sim_dict[k] = v[0]
        print(sim_dict)


    if sim_file and mes_file:
        result_text = text_to_format.format(s_filename=sim_file,
                            s_time=sim_dict['time'],
                            s_vt=sim_dict['vt'],
                            s_p=sim_dict['pg'],
                            s_q=sim_dict['qg'],
                            s_efd=sim_dict['efd'],
                            s_ifd=sim_dict['ifd'],
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
                            s_time=sim_dict['time'],
                            s_vt=sim_dict['vt'],
                            s_p=sim_dict['pg'],
                            s_q=sim_dict['qg'],
                            s_efd=sim_dict['efd'],
                            s_ifd=sim_dict['ifd']
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

