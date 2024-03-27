# ScriptListener.py, Charlie Jordan, 2/2/2024
# Background thread that listens to a queue that the
# backend scripts can access and add to. Handles
# both asynchronous and synchronous requests from
# the script

import threading
import traceback
import queue
import re

from urllib.error import URLError
from urllib.request import urlopen
import tkinter.messagebox as messagebox

import supertool.consts as consts
from supertool.Version import Version
from supertool.pslf_scripts.Super_Tool import ScriptQueue, SuperToolMessage

class ScriptListener(threading.Thread):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.daemon = True
        self.running = False
    
    def run(self):
        self.running = True
        while self.running:
            # try to grab something from the queue, if there's nothing reset
            # the loop
            try:
                message = ScriptQueue.get(timeout=0.5)
            except queue.Empty:
                continue
            
            print(f">>> ScriptListener Processing:\n>>> {message}")
            try:
                if message.type == 'ynprompt':
                    message.return_val = messagebox.askyesno(message=message.data)
                    message.done()
                elif message.type == 'scriptalreadyrunning':
                    messagebox.showinfo(message=message.data)
                elif message.type == 'check4update':
                    self.check_for_update()
                elif message.type == 'stopscriptlistener':
                    print("stopscriptlistener")
                    message.done()
                    self.running = False
                elif message.type == 'setstatus':
                    self.status(message.data)
                    self.root.after(5, message.done)
                elif message.type == 'compress':
                    message.data() # data is a function
                    
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
        
        print(">>> ScriptListener Closing...\n")
    
    def check_for_update(self):
        self.status("Checking for Updates...", spin=True)
        try:
            new_url = urlopen(consts.GITHUB_REPO, timeout=3).url
            if len(new_url) > 40 and "github" in new_url:
                ver = new_url.split('/')[-1]
                m = re.match(r'^v(\d+)\.(\d+)\.(\d+)$', ver)
                if m: # request worked
                    remote_ver = Version(*(int(m.group(i)) for i in [1,2,3]))
                    if remote_ver > consts.VERSION:
                        text = f"Super Tool Version:  {consts.VERSION}, Update to version {remote_ver}"
                    elif remote_ver < consts.VERSION:
                        text = f"Super Tool Version:  {consts.VERSION}, Ahead of version {remote_ver}"
                    else:
                        text = f"Super Tool Version: {consts.VERSION}, Up to date"
                    self.status(text)
                    # self.root.set_status(text)
                    print(text)
                else: # request failed, printout update checker failed
                    self.status("Update Check Failed.")
            else: # request failed, printout update checker failed
                self.status("Update Check Failed.")
        
        except (URLError, TimeoutError):
            self.status("Update Check Failed.")
    
    def status(self, *args, **kwargs):
        if self.root.main_loop_running:
            self.root.set_status(*args, **kwargs)