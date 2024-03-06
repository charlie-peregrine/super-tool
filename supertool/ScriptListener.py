# ScriptListener.py, Charlie Jordan, 2/2/2024
# Background thread that listens to a queue that the
# backend scripts can access and add to. Handles
# both asynchronous and synchronous requests from
# the script

import threading
import traceback
from supertool.pslf_scripts.Super_Tool import ScriptQueue, SuperToolMessage
import queue

from urllib.error import URLError
from urllib.request import urlopen
import tkinter.messagebox as messagebox
import supertool.consts as consts
import re

class ScriptListener(threading.Thread):
    def __init__(self, root):
        super().__init__()
        self.root = root
    
    def run(self):
        while self.root.running:
            # try to grab something from the queue, if there's nothing reset
            # the loop
            try:
                message = ScriptQueue.get(timeout=0.5)
            except queue.Empty:
                continue
            
            print(f">>> ScriptListener Processing:\n>>> {message}")
            try:
                if message.type == 'ynprompt':
                    message.return_val = messagebox.askyesno(message=message.text)
                    message.done()
                if message.type == 'scriptalreadyrunning':
                    messagebox.showinfo(message=message.text)
                if message.type == 'check4update':
                    self.check_for_update()
                
                else:
                    raise TypeError("SuperToolMessage " + message
                                    + " does not have a valid type")
            except Exception as err:
                print(">>> ScriptListener Encountered an error while processing:")
                print(f">>> {message}")
                print("vvv Error message vvv\n")
                traceback.print_exception(err)
                print("\n^^^ End Error message ^^^")
                
                if message.waiting():
                    message.done()
            
            
            print(f">>> ScriptListener Done Processing:\n>>> {message}")
            ScriptQueue.task_done()
    
    def check_for_update(self):
        try:
            new_url = urlopen(consts.GITHUB_REPO, timeout=3).url
            if len(new_url) > 40 and "github" in new_url:
                ver = new_url.split('/')[-1]
                m = re.match(r'^v(\d+)\.(\d+)\.(\d+)$', ver)
                if m: # request worked
                    remote_ver = (int(m.group(i)) for i in [1,2,3])
                    for remote, local in zip(remote_ver, consts.VERSION):
                        if remote > local:
                            # need update
                            print(f"Update to version {m.group(0)}")
                            break
                        if local > remote:
                            # ahead?
                            print(f"Ahead of version {m.group(0)}")
                            break
                    else:
                        # same version number
                        print("Versions are the same.")
                        
                else: # request failed, printout update checker failed
                    pass
            else: # request failed, printout update checker failed
                pass
        
        except (URLError, TimeoutError):
            pass
    