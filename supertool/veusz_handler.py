# veusz_handler.py, Charlie Jordan, 1/5/2023
# handles the veusz program calls and passing the right files
# to veusz. Also modifies the fvsz (vsz files with python format
# blocks in them) to use the right headers and csv files

import supertool.consts as consts

#VEUSZ_PATH = config.VEUSZ_PATH # "C:/Program Files (x86)/Veusz/"
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

# @TODO add veusz_path to user path, prolly done in an install script

import subprocess
import re

# mes_file_name = 'C:/Users/charlie/Downloads/SampleProject/SampleFolder/Voltage_Reference.csv'
# sim_file_name = 'C:/Users/charlie/Downloads/SampleProject/SampleFolder/Voltage_Reference_sim.csv'


def replace_dict(d, k, m, default='y'):
    if d[k]:
        d[k] = '`' + d[k] + '`' + m
    else:
        d[k] = default


def plot_voltage_reference(*, sim_dict={}, mes_dict={}): #sim_file='', mes_file=''):
    with open("veusz_files/Voltage_Reference.fvsz", 'r') as file:
        fvsz_text = file.read()
    
    for k,v in sim_dict.items():
        print(k, v, sim_dict[k])
        if v[1]:
            sim_dict[k] = '`' + v[0] + '`' + v[1]
        elif v[0]:
            sim_dict[k] = v[0]
        else:
            sim_dict[k] = 'y'
    
    for k,v in mes_dict.items():
        if v[1]:
            mes_dict[k] = '`' + v[0] + '`' + v[1]
        elif v[0]:
            mes_dict[k] = v[0]
        else:
            mes_dict[k] = 'y'
    
    

    if sim_dict and mes_dict:
        result_text = fvsz_text.format(s_filename=sim_dict['file'],
                            s_time=sim_dict['time'],
                            s_vt=sim_dict['vt'],
                            s_p=sim_dict['pg'],
                            s_q=sim_dict['qg'],
                            s_efd=sim_dict['efd'],
                            s_ifd=sim_dict['ifd'],
                            m_filename=mes_dict['file'],
                            m_time=mes_dict['time'],
                            m_vt=mes_dict['vt'],
                            m_p=mes_dict['pg'],
                            m_q=mes_dict['qg'],
                            m_efd=mes_dict['efd'],
                            m_ifd=mes_dict['ifd']
                            )
    elif sim_dict:
        pattern = r"Add\('xy', name='Measured'(?:.*\n)+?To\('\.\.'\)\n|.*{m_filename}.*\n"
        fvsz_text = re.sub(pattern, '', fvsz_text, flags=re.MULTILINE)
        
        result_text = fvsz_text.format(s_filename=sim_dict['file'],
                            s_time=sim_dict['time'],
                            s_vt=sim_dict['vt'],
                            s_p=sim_dict['pg'],
                            s_q=sim_dict['qg'],
                            s_efd=sim_dict['efd'],
                            s_ifd=sim_dict['ifd']
                            )
    elif mes_dict:
        pattern = r"Add\('xy', name='Simulated'(?:.*\n)+?To\('\.\.'\)\n|.*{s_filename}.*\n"
        fvsz_text = re.sub(pattern, '', fvsz_text, flags=re.MULTILINE)
        
        result_text = fvsz_text.format(m_filename=mes_dict['file'],
                            m_time=mes_dict['time'],
                            m_vt=mes_dict['vt'],
                            m_p=mes_dict['pg'],
                            m_q=mes_dict['qg'],
                            m_efd=mes_dict['efd'],
                            m_ifd=mes_dict['ifd']
                            )
    else:
        result_text = ''
        print("uh oh no file names")
        

    if result_text:
        # @TODO make the filename unique enough
        with open("veusz_files/.graph_output.vsz", 'w') as file:
            file.write(result_text)

        process = subprocess.Popen('veusz.exe ./veusz_files/.graph_output.vsz', env=consts.MY_ENV, shell=True)
        
        return process
        
        # process.kill()

def plot_steady_state(sim_dict={}, mes_dict=None):
    
    if not sim_dict:
        print("no file to get steady state graphs from! uh oh")
        return
    
    for k,v in sim_dict.items():
        print(k, v, sim_dict[k])
        if v[1]:
            sim_dict[k] = '`' + v[0] + '`' + v[1]
        elif v[0]:
            sim_dict[k] = v[0]
        else:
            sim_dict[k] = 'y'
    
    with open("veusz_files/Steady_State.fvsz", 'r') as file:
        fvsz_text = file.read()

    result_text = fvsz_text.format(filename=sim_dict['file'], s_header=sim_dict['sim'],
                                   m_header=sim_dict['mes'])
    
    print("If there is no if and ef supplied to the script then veusz will complain here")
    
    with open("veusz_files/.graph_output.vsz", 'w') as file:
        file.write(result_text)
    process = subprocess.Popen('veusz.exe ./veusz_files/.graph_output.vsz', env=consts.MY_ENV, shell=True)
        
    return process
        
def plot_current_interruption(*, sim_dict={}, mes_dict={}):
    with open("veusz_files/Current_Interruption.fvsz", 'r') as file:
        fvsz_text = file.read()
    
    for k,v in sim_dict.items():
        print(k, v, sim_dict[k])
        if v[1]:
            sim_dict[k] = '`' + v[0] + '`' + v[1]
        elif v[0]:
            sim_dict[k] = v[0]
        else:
            sim_dict[k] = 'y'
    
    for k,v in mes_dict.items():
        if v[1]:
            mes_dict[k] = '`' + v[0] + '`' + v[1]
        elif v[0]:
            mes_dict[k] = v[0]
        else:
            mes_dict[k] = 'y'
    # s_time, m_time, s_filename, m_filename
    
    if sim_dict and mes_dict:
        result_text = fvsz_text.format(s_filename=sim_dict['file'],
                            s_time=sim_dict['time'],
                            s_vt=sim_dict['vt'],
                            s_p=sim_dict['pg'],
                            s_q=sim_dict['qg'],
                            s_efd=sim_dict['efd'],
                            s_ifd=sim_dict['ifd'],
                            s_freq=sim_dict['freq'],
                            m_filename=mes_dict['file'],
                            m_time=mes_dict['time'],
                            m_vt=mes_dict['vt'],
                            m_p=mes_dict['pg'],
                            m_q=mes_dict['qg'],
                            m_efd=mes_dict['efd'],
                            m_ifd=mes_dict['ifd'],
                            m_freq=mes_dict['freq']
                            )
    elif sim_dict:
        pattern = r"Add\('xy', name='Measured'(?:.*\n)+?To\('\.\.'\)\n|.*{m_filename}.*\n"
        fvsz_text = re.sub(pattern, '', fvsz_text, flags=re.MULTILINE)
        
        result_text = fvsz_text.format(s_filename=sim_dict['file'],
                            s_time=sim_dict['time'],
                            s_vt=sim_dict['vt'],
                            s_p=sim_dict['pg'],
                            s_q=sim_dict['qg'],
                            s_efd=sim_dict['efd'],
                            s_ifd=sim_dict['ifd'],
                            s_freq=sim_dict['freq']
                            )
    elif mes_dict:
        pattern = r"Add\('xy', name='Simulated'(?:.*\n)+?To\('\.\.'\)\n|.*{s_filename}.*\n"
        fvsz_text = re.sub(pattern, '', fvsz_text, flags=re.MULTILINE)
        
        result_text = fvsz_text.format(m_filename=mes_dict['file'],
                            m_time=mes_dict['time'],
                            m_vt=mes_dict['vt'],
                            m_p=mes_dict['pg'],
                            m_q=mes_dict['qg'],
                            m_efd=mes_dict['efd'],
                            m_ifd=mes_dict['ifd'],
                            m_freq=mes_dict['freq']
                            )
    else:
        result_text = ''
        print("uh oh no file names")

    if result_text:
        # @TODO make the filename unique enough
        with open("veusz_files/.graph_output.vsz", 'w') as file:
            file.write(result_text)

        process = subprocess.Popen('veusz.exe ./veusz_files/.graph_output.vsz', env=consts.MY_ENV, shell=True)
        
        return process
        
        # process.kill()