# ParamView.py, Charlie Jordan, 1/12/2024
# Graph Parameter modification pane of the main supertool gui window

import re
import tkinter as tk
from tkinter import ttk

from SuperToolFrames import ScrollFrame

# subclass of frame that holds the plot parameter view
# the goal of this view is to allow the user to manipulate
# the plotted graphs to be more visually appealing in order
# to make sense as graph objects
# currently a WIP  
class ParamView(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent, borderwidth=5, relief='groove',
                         height=100, width=100)

        # param_text = ttk.Label(self, text="plot params")
        # param_text.grid(row=0,column=0)
        
        self.graph_button = ttk.Button(self, text="Show Graphs",
                                        command=self.graph)
        self.graph_button.grid(row=0, column=0)

        # self.scroller = ScrollFrame(self)
        # self.scroll_frame = self.scroller.frame
        self.sim_widgets = {}
        self.mes_blobs = []
        
        self.sim_frame = ttk.Frame(self)
        # self.mes_frame = ttk.Frame(self)
        self.sim_frame.grid(row=1, column=0, sticky='nesw')
        # self.mes_frame.grid(row=2, column=0, sticky='nesw')
        
        self.render()
        
    def render(self):
        
        foc = self.parent.focused_test
        
        self.sim_frame.grid_remove()
        # self.mes_frame.grid_remove()
        
        
        if foc:
            if foc.plot_sim_file and foc[foc.plot_sim_file]:
                # build sim frame. need:
                    # plot that needs a header
                    # header dropdown menu
                    # multiplication menu (support +,-,/,*)
                self.sim_widgets.clear()
        
                for widget in self.sim_frame.winfo_children():
                    widget.destroy()
                
                with open(foc[foc.plot_sim_file], 'r') as file:
                    header_list = [s.strip() for s in file.readline()[:-2].split(',')]
                    header_text = '\n'.join(header_list)
                    max_width = max([len(s) for s in header_list] + [20])
                    max_width = int(max_width * .75)
                
                
                for i, (key, regex, longname) in enumerate(foc.header_info):
                    sim_label = ttk.Label(self.sim_frame, text=longname)
                    sim_label.grid(row=1+i, column=0)
                    
                    # @TODO save user input headers instead of finding them
                    found_headers = re.findall(regex, header_text, flags=re.IGNORECASE)
                        
                    sim_dropdown = ttk.Combobox(
                        self.sim_frame, values=header_list, width=max_width, 
                        state='readonly'
                    )
                    if found_headers:
                        found_header = found_headers[0]
                        sim_dropdown.current(header_list.index(found_header))
                    sim_dropdown.grid(row=1+i, column=1)
                    
                    sim_entry = ttk.Entry(self.sim_frame, width=7)
                    sim_entry.grid(row=1+i, column=2)
                    
                    self.sim_widgets[key] = (sim_label, sim_dropdown, sim_entry)
                
                self.sim_frame.grid()
                
                self.show_simulated_headers()
            
            # if foc.plot_mes_file:
            #     self.show_measured_headers()

    def show_simulated_headers(self):
        foc = self.parent.focused_test
        
        

    # def show_measured_headers(self):
        
    #     self.mes_blobs.clear()
        
    #     for widget in self.mes_frame.winfo_children():
    #         widget.destroy()

    #     self.mes_frame.grid()
    #     for i in range(4):
    #         l = ttk.Label(self.mes_frame, text="hey " + str(i))
    #         l.grid(row=4+i, column=0)
    #         self.mes_blobs.append(l)
            
    #         e1 = ttk.Combobox(self.mes_frame)
    #         e1.grid(row=4+i, column=1)
    #         self.mes_blobs.append(e1)
            
    #         e2 = ttk.Entry(self.mes_frame)
    #         e2.grid(row=4+i, column=2)
    #         self.mes_blobs.append(e2)
    
    def graph(self):
        
        if not self.parent.focused_test:
            print("no focused test yet")
            return
        
        self.parent.focused_test.plot()
        
        
        