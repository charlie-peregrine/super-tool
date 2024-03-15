# ParamView.py, Charlie Jordan, 1/12/2024
# Graph Parameter modification pane of the main supertool gui window

import os
import re
import tkinter as tk
from tkinter import ttk
from idlelib.tooltip import Hovertip

import supertool.consts as consts
from supertool.SuperToolFrames import ScrollFrame

# subclass of frame that holds the plot parameter view
# the goal of this view is to allow the user to manipulate
# the plotted graphs to be more visually appealing in order
# to make sense as graph objects
# currently a WIP  
class ParamView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=5, relief='groove',
                         height=100, width=100)
        self.parent = parent.master
        
        self.graph_button = ttk.Button(self, text="Show Graphs",
                                        command=self.graph)
        self.graph_button.grid(row=0, column=0)

        self.graph_button.bind("<3>", lambda e:
            self.parent.graph_menu.post(e.x_root, e.y_root))
        self.graph_button_hover = Hovertip(self.graph_button, hover_delay=consts.HOVER_DELAY,
            text="Right click to open Run Menu")

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
                
        self.parent.update_pane_widths()
    
    def render_mes_frame(self):
        self.mes_frame.grid_remove()
        self.mes_widgets.clear()
        for widget in self.mes_frame.winfo_children():
            widget.destroy()
        
        if self.foc:
            if self.foc.plot_mes_file and self.foc[self.foc.plot_mes_file]:
                self.build_frame(self.foc.plot_mes_file, self.mes_frame, self.mes_widgets, self.foc.mes_headers)
        
        self.parent.update_pane_widths() # @TODO do we need this to run twice?
            

    # subroutine to make building cleaner
    def build_frame(self, plot_name, frame, widgets, test_headers):
        # @TODO error check for multiplication menu (support +,-,/,*)
        
        # @check that file exists here or earlier (on read and on select?)
        if not os.path.exists(self.foc.attrs[plot_name].get()):
            # @TODO tell the user somehow that this is bad
            print(self.foc.attrs[plot_name].get(), "does not exist")
            return
        
        with open(self.foc.attrs[plot_name].get(), 'r', encoding='utf-8-sig') as file:
            line = file.readline()
            if line[-1] == '\n': # trim trailing newline
                line = line[:-1]
            header_list = [s.strip() for s in line.split(',')]
            header_list = [s for s in header_list if s]
            header_text = '\n'.join(header_list)
            max_width = max([len(s) for s in header_list] + [20])
            max_width = int(max_width * .83)
        
        
        for i, (key, regex, longname) in enumerate(self.foc.header_info):
            longname_label = ttk.Label(frame, text=longname)
            longname_label.grid(row=1+i, column=0)
            
            header_dropdown = ttk.Combobox(
                frame, values=header_list, width=max_width, 
                state='readonly'
            )
            
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
    
    def graph(self, save_on_graph=True):
        
        if not self.foc:
            print("no focused test yet")
            self.parent.set_status("No focused test to graph!", error=True)
            return
        
        # save the project before graphing
        if save_on_graph:
            self.parent.save_project()
        
        sim_data = {}
        sim_data['ready'] = False # is it ok to graph this data
        if self.sim_widgets:
            for k, (_,d,e) in self.sim_widgets.items():
                sim_data[k] = (d.get(), e.get())
            # veusz files need paths to use / instead of \
            file_path = self.foc.attrs[self.foc.plot_sim_file].get().replace("\\", "/")
            sim_data['file'] = (file_path, '')
            sim_data['ready'] = True
        
        for k,v in sim_data.items():
            print(k, v)
        
        mes_data = {}
        mes_data['ready'] = False
        if self.mes_widgets:
            for k, (_,d,e) in self.mes_widgets.items():
                mes_data[k] = (d.get(), e.get())
            # veusz files need paths to use / instead of \
            file_path = self.foc.attrs[self.foc.plot_mes_file].get().replace("\\", "/")
            mes_data['file'] = (file_path, '')
            mes_data['ready'] = True # is it ok to graph this data
        
        for k,v in mes_data.items():
            print(k, v)
        
        warnings = []
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
                warnings.append(f"Warning: Minimum x value of {x_min} is invalid, defaulting to Auto.")
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
                warnings.append(f"Warning: Maximum x value of {x_max} is invalid, defaulting to Auto.")
                sim_data['xmax'] = "'Auto'"
                mes_data['xmax'] = "'Auto'"
        
        for w in warnings:
            print(w)
            self.parent.set_status(w)
        
        self.parent.set_status("Plotting graphs. " + " ".join(warnings))
        self.foc.plot(sim_dict=sim_data, mes_dict=mes_data)
        
    