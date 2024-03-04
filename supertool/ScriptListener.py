# ScriptListener.py, Charlie Jordan, 2/2/2024
# Background thread that listens to a queue that the
# backend scripts can access and add to. Handles
# both asynchronous and synchronous requests from
# the script

import threading
import traceback
from supertool.pslf_scripts.Super_Tool import ScriptQueue, SuperToolMessage
import queue

import tkinter.messagebox as messagebox

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