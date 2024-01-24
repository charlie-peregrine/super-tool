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
        self.sim_frame.grid(row=1, column=0, sticky='nesw')
        self.mes_frame.grid(row=2, column=0, sticky='nesw')
        
        self.render()
        
    def render(self):
        
        self.render_sim_frame()
        self.render_mes_frame()


    def render_sim_frame(self):
        self.sim_frame.grid_remove()
        self.sim_widgets.clear()
        for widget in self.sim_frame.winfo_children():
            widget.destroy()
        
        foc = self.parent.focused_test
        
        if foc:
            # @TODO watch foc[foc.plot_sim_file] to update sim frame if necessary
            if foc.plot_sim_file and foc[foc.plot_sim_file]:
                self.build_frame(foc.plot_sim_file, self.sim_frame, self.sim_widgets, foc.sim_headers)
    
    def render_mes_frame(self):
        self.mes_frame.grid_remove()
        self.mes_widgets.clear()
        for widget in self.mes_frame.winfo_children():
            widget.destroy()
        
        foc = self.parent.focused_test
            
        if foc:
            if foc.plot_mes_file and foc[foc.plot_mes_file]:
                self.build_frame(foc.plot_mes_file, self.mes_frame, self.mes_widgets, foc.mes_headers)
        
            

    # subroutine to make building cleaner
    def build_frame(self, plot_name, frame, widgets, test_headers):
        # @TODO error check for multiplication menu (support +,-,/,*)
        
        foc = self.parent.focused_test
        
        with open(foc[plot_name], 'r') as file:
            header_list = [s.strip() for s in file.readline()[:-2].split(',')]
            header_text = '\n'.join(header_list)
            max_width = max([len(s) for s in header_list] + [20])
            max_width = int(max_width * .75)
        
        
        for i, (key, regex, longname) in enumerate(foc.header_info):
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
                
            # if not try_dropdown(test_headers[key][0].get()):
            
            header_dropdown.grid(row=1+i, column=1)
            
            expr_entry = ttk.Entry(frame, width=7, textvariable=test_headers[key][1])
            expr_entry.grid(row=1+i, column=2)
            
            widgets[key] = (longname_label, header_dropdown, expr_entry)
        
        frame.grid()
    
    def graph(self):
        
        foc = self.parent.focused_test
        
        if not foc:
            print("no focused test yet")
            return
        
        sim_data = {}
        if self.sim_widgets:
            for k, (l,d,e) in self.sim_widgets.items():
                sim_data[k] = (d.get(), e.get())
            sim_data['file'] = (foc[foc.plot_sim_file], '')
        
        print(sim_data)
        
        mes_data = {}
        if self.mes_widgets:
            for k, (l,d,e) in self.mes_widgets.items():
                mes_data[k] = (d.get(), e.get())
            mes_data['file'] = (foc[foc.plot_mes_file], '')
        
        print(mes_data)
        
        foc.plot(sim_dict=sim_data, mes_dict=mes_data)
        
    
    def get_mes_header_info(self):
        return {}