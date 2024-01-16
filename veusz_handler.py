# veusz_handler.py, Charlie Jordan, 1/5/2023
# handles the veusz program calls and passing the right files
# to veusz. Also modifies the fvsz (vsz files with python format
# blocks in them) to use the right headers and csv files

from config import *

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


def plot_voltage_reference(sim_file='', mes_file=''):
    with open("veusz_files/Voltage_Reference.fvsz", 'r') as file:
        fvsz_text = file.read()

    # get column titles for the simulated data
    sim_dict = {}
    if sim_file:
        with open(sim_file, 'r') as file:
            headers = file.readline().split(',')
            headers = '\n'.join([s.strip() for s in headers])
            
        sim_dict['time'] = re.findall(r'.*time.*', headers, flags=re.IGNORECASE)
        sim_dict['vt'] = re.findall( r'(?=.*vt)(?=.*1)(?=.*gen).*', headers, flags=re.IGNORECASE)
        sim_dict['pg'] = re.findall( r'(?=.*pg)(?=.*1)(?=.*gen).*', headers, flags=re.IGNORECASE)
        sim_dict['qg'] = re.findall( r'(?=.*qg)(?=.*1)(?=.*gen).*', headers, flags=re.IGNORECASE)
        sim_dict['efd'] = re.findall(r'(?=.*efd)(?=.*1)(?=.*gen).*', headers, flags=re.IGNORECASE)
        sim_dict['ifd'] = re.findall(r'(?=.*ifd?)(?=.*1)(?=.*(?:gen|es)).*', headers, flags=re.IGNORECASE)
        # sim_dict['time'] = re.findall(r'.*time.*', headers, flags=re.IGNORECASE)
        # sim_dict['vt'] = re.findall(r'"vt\s+1"?gen.*', headers, flags=re.IGNORECASE)
        # sim_dict['pg'] = re.findall(r'"pg\s+1"?gen.*', headers, flags=re.IGNORECASE)
        # sim_dict['qg'] = re.findall(r'"qg\s+1"?gen.*', headers, flags=re.IGNORECASE)
        # sim_dict['efd'] = re.findall(r'"efd\s+1"?gen.*', headers, flags=re.IGNORECASE)
        # sim_dict['ifd'] = re.findall(r'"ifd\s+1"?gen.*', headers, flags=re.IGNORECASE)

        for k,v in sim_dict.items():
            # print(len(sim_dict[k]), sim_dict[k])
            if len(sim_dict[k]) == 0:
                print(f"blah blah simulated {k} has zero oops")
                sim_dict[k] = ''
            else:
                if len(sim_dict[k]) > 1:
                    print(f"blah blah simulated {k} too many, picking the first one")
                sim_dict[k] = v[0]
        # print(sim_dict)
        
        # modify necessary sim header names for veusz use
        replace_dict(sim_dict, 'vt', '*14.4')
        replace_dict(sim_dict, 'efd', '*720*0.18')
        replace_dict(sim_dict, 'ifd', '*740')

    # get measured headers
    mes_dict = {}
    if mes_file:
        with open(mes_file, 'r') as file:
            headers = file.readline().split(',')
            headers = '\n'.join([s.strip() for s in headers])
        
        mes_dict['time'] = re.findall(r'.*(?:time|seconds).*', headers, flags=re.IGNORECASE)
        mes_dict['vt'] = re.findall( r'(?=.*vave).*', headers, flags=re.IGNORECASE)
        mes_dict['pg'] = re.findall( r'(?=.*kw).*', headers, flags=re.IGNORECASE)
        mes_dict['qg'] = re.findall( r'(?=.*kvar).*', headers, flags=re.IGNORECASE)
        mes_dict['efd'] = re.findall(r'(?=.*vfd).*', headers, flags=re.IGNORECASE)
        mes_dict['ifd'] = re.findall(r'(?=.*ifd).*', headers, flags=re.IGNORECASE)
    
        for k,v in mes_dict.items():
            if len(mes_dict[k]) == 0:
                print(f"blah blah measured {k} has zero oops")
                mes_dict[k] = ''
            else:
                if len(mes_dict[k]) > 1:
                    print(f"blah blah measured {k} too many, picking the first one")
                mes_dict[k] = v[0]
    
        replace_dict(mes_dict, 'vt', '*14.4')
        replace_dict(mes_dict, 'pg', '*166.75')
        replace_dict(mes_dict, 'qg', '*166.75')
        replace_dict(mes_dict, 'efd', '*250')
        replace_dict(mes_dict, 'ifd', '*1362')
        

    if sim_file and mes_file:
        result_text = fvsz_text.format(s_filename=sim_file,
                            s_time=sim_dict['time'],
                            s_vt=sim_dict['vt'],
                            s_p=sim_dict['pg'],
                            s_q=sim_dict['qg'],
                            s_efd=sim_dict['efd'],
                            s_ifd=sim_dict['ifd'],
                            m_filename=mes_file,
                            m_time=mes_dict['time'],
                            m_vt=mes_dict['vt'],
                            m_p=mes_dict['pg'],
                            m_q=mes_dict['qg'],
                            m_efd=mes_dict['efd'],
                            m_ifd=mes_dict['ifd']
                            )
    elif sim_file:
        pattern = r"Add\('xy', name='Measured'(?:.*\n)+?To\('\.\.'\)\n|.*{m_filename}.*\n"
        fvsz_text = re.sub(pattern, '', fvsz_text, flags=re.MULTILINE)
        
        result_text = fvsz_text.format(s_filename=sim_file,
                            s_time=sim_dict['time'],
                            s_vt=sim_dict['vt'],
                            s_p=sim_dict['pg'],
                            s_q=sim_dict['qg'],
                            s_efd=sim_dict['efd'],
                            s_ifd=sim_dict['ifd']
                            )
    elif mes_file:
        pattern = r"Add\('xy', name='Simulated'(?:.*\n)+?To\('\.\.'\)\n|.*{s_filename}.*\n"
        fvsz_text = re.sub(pattern, '', fvsz_text, flags=re.MULTILINE)
        
        result_text = fvsz_text.format(m_filename=mes_file,
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
        with open("veusz_files/.blahg.vsz", 'w') as file:
            file.write(result_text)

        process = subprocess.Popen('"' + VEUSZ_PATH + '/veusz.exe" ./veusz_files/.blahg.vsz') #, shell=True)
        
        return process
        
        # process.kill()

def plot_steady_state(out_file):
    
    if not out_file:
        print("no file to get steady state graphs from! uh oh")
        return
    
    with open("veusz_files/Steady_State.fvsz", 'r') as file:
        fvsz_text = file.read()

    with open(out_file, 'r') as file:
        headers = [s.strip() for s in file.readline().split(',')]

    # 6 -> sim, 9 -> measured
    result_text = fvsz_text.format(filename=out_file, s_header=headers[6],
                                   m_header=headers[9])
    
    with open("veusz_files/.blahg.vsz", 'w') as file:
        file.write(result_text)
    process = subprocess.Popen('"' + VEUSZ_PATH + '/veusz.exe" ./veusz_files/.blahg.vsz') #, shell=True)
        
    return process
        
