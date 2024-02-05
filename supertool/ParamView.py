# ParamView.py, Charlie Jordan, 1/12/2024
# Graph Parameter modification pane of the main supertool gui window

import re
import tkinter as tk
from tkinter import ttk

from supertool.SuperToolFrames import ScrollFrame

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
        
        self.graph_button = ttk.Button(self, text="Show Graphs",
                                        command=self.graph)
        self.graph_button.grid(row=0, column=0)

        # self.scroller = ScrollFrame(self)
        # self.scroll_frame = self.scroller.frame
        self.sim_widgets = {}
        self.mes_widgets = {}
        
        self.sim_frame = ttk.Frame(self)
        self.mes_frame = ttk.Frame(self)
        self.min_max_frame = ttk.Frame(self)
        self.sim_frame.grid(row=1, column=0, sticky='nesw', pady=3)
        self.mes_frame.grid(row=2, column=0, sticky='nesw', pady=3)
        self.min_max_frame.grid(row=3, column=0, sticky='nesw', pady=3)
        
        # self.foc = None
        
        self.render()
        
    def render(self):
        # @TODO make exception for steady state test type
        
        self.foc = self.parent.focused_test
        
        for widget in self.min_max_frame.winfo_children():
            widget.destroy()
            
        if self.foc:
            min_max_label = ttk.Label(self.min_max_frame, text="X Range: ")
            min_max_label.grid(row=0, column=0)
            min_entry = ttk.Entry(self.min_max_frame,
                    textvariable=self.foc.x_range_min, width=8)
            min_entry.grid(row=0, column=1)
            dash_label = ttk.Label(self.min_max_frame, text=" - ")
            dash_label.grid(row=0, column=2)
            max_entry = ttk.Entry(self.min_max_frame,
                    textvariable=self.foc.x_range_max, width=8)
            max_entry.grid(row=0, column=3)
        
        
        self.render_sim_frame()
        self.render_mes_frame()


    def render_sim_frame(self):
        self.sim_frame.grid_remove()
        self.sim_widgets.clear()
        for widget in self.sim_frame.winfo_children():
            widget.destroy()
        
        if self.foc:
            # @TODO watch foc[foc.plot_sim_file] to update sim frame if necessary
            if self.foc.plot_sim_file and self.foc[self.foc.plot_sim_file]:
                self.build_frame(self.foc.plot_sim_file, self.sim_frame, self.sim_widgets, self.foc.sim_headers)
    
    def render_mes_frame(self):
        self.mes_frame.grid_remove()
        self.mes_widgets.clear()
        for widget in self.mes_frame.winfo_children():
            widget.destroy()
        
        if self.foc:
            if self.foc.plot_mes_file and self.foc[self.foc.plot_mes_file]:
                self.build_frame(self.foc.plot_mes_file, self.mes_frame, self.mes_widgets, self.foc.mes_headers)
        
            

    # subroutine to make building cleaner
    def build_frame(self, plot_name, frame, widgets, test_headers):
        # @TODO error check for multiplication menu (support +,-,/,*)
        
        # @TODO check that file exists here or earlier (on read and on select?)
        
        with open(self.foc[plot_name], 'r', encoding='utf-8-sig') as file:
            line = file.readline()
            if line[-1] == '\n': # trim trailing newline
                line = line[:-1]
            header_list = [s.strip() for s in line.split(',')]
            header_list = [s for s in header_list if s]
            header_text = '\n'.join(header_list)
            max_width = max([len(s) for s in header_list] + [20])
            max_width = int(max_width * .75)
        
        
        for i, (key, regex, longname) in enumerate(self.foc.header_info):
            longname_label = ttk.Label(frame, text=longname)
            longname_label.grid(row=1+i, column=0)
            
            header_dropdown = ttk.Combobox(
                frame, values=header_list, width=max_width, 
                state='readonly'
            )
            
            # @TODO save user input headers instead of finding them
            
            # try to set the header to the saved one, and if that fails
            # try to set it to an automatically found one
            def try_dropdown(val):
                try:
                    i = header_list.index(val)
                    header_dropdown.current(i)
                    return True
                except ValueError:
                    pass
                return False

            if test_headers[key][0].get() not in header_list:
                
                found_headers = re.findall(regex, header_text, flags=re.IGNORECASE)
                if found_headers:
                    # @TODO have tkinter say that a header got overwritten here
                    test_headers[key][0].set(found_headers[0])
                else:
                    test_headers[key][0].set('')
            header_dropdown.config(textvariable=test_headers[key][0])
                
            
            header_dropdown.grid(row=1+i, column=1)
            
            expr_entry = ttk.Entry(frame, width=7, textvariable=test_headers[key][1])
            expr_entry.grid(row=1+i, column=2)
            
            widgets[key] = (longname_label, header_dropdown, expr_entry)
        
        frame.grid()
    
    def graph(self):
        
        if not self.foc:
            print("no focused test yet")
            return
        
        sim_data = {}
        sim_data['ready'] = False # is it ok to graph this data
        if self.sim_widgets:
            for k, (l,d,e) in self.sim_widgets.items():
                sim_data[k] = (d.get(), e.get())
            sim_data['file'] = (self.foc[self.foc.plot_sim_file], '')
            sim_data['ready'] = True
        
        print(sim_data)
        
        mes_data = {}
        mes_data['ready'] = False
        if self.mes_widgets:
            for k, (l,d,e) in self.mes_widgets.items():
                mes_data[k] = (d.get(), e.get())
            mes_data['file'] = (self.foc[self.foc.plot_mes_file], '')
            mes_data['ready'] = True # is it ok to graph this data
        
        print(mes_data)
        
        x_min = self.foc.x_range_min.get()
        if x_min.lower() == '' or x_min.lower() == 'auto':
            sim_data['xmin'] = "'Auto'"
            mes_data['xmin'] = "'Auto'"
        else:
            try:
                x_min = float(x_min)
                sim_data['xmin'] = x_min
                mes_data['xmin'] = x_min
            except ValueError:
                print(f"X Minimum value of {x_min} is invalid, defaulting to Auto")
                sim_data['xmin'] = "'Auto'"
                mes_data['xmin'] = "'Auto'"
        
        x_max = self.foc.x_range_max.get()
        if x_max.lower() == '' or x_max.lower() == 'auto':
            sim_data['xmax'] = "'Auto'"
            mes_data['xmax'] = "'Auto'"
        else:
            try:
                x_max = float(x_max)
                sim_data['xmax'] = x_max
                mes_data['xmax'] = x_max
            except ValueError:
                print(f"X Maximum value of {x_max} is invalid, defaulting to Auto")
                sim_data['xmax'] = "'Auto'"
                mes_data['xmax'] = "'Auto'"
        
        self.foc.plot(sim_dict=sim_data, mes_dict=mes_data)
        
    