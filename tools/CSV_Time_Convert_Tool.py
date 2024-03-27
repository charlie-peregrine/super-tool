

import os

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd

import pandas as pd
#import numpy as np
#from numpy import genfromtxt
#import time


dir_path = os.path.dirname(os.path.realpath(__file__))
conf_geometry = "geometry.conf"
conf_geometry = os.path.join(dir_path,conf_geometry)
# csv_filename = ""

Header_Row = "Header_Row"
Timestamp_Column = "Timestamp_Column"


def select_file():
    filetypes   = (('csv files', '*.csv'),('All files', '*.*'))
    csv_filenames = fd.askopenfilenames(parent=window, title='Select multiple files',initialdir="",filetypes=filetypes)
    # csv_filenames = list(csv_filenames) # unnecessary? askopen... returns a list
    print("csv_filenames: ",csv_filenames)
    
    for csv_filename in csv_filenames:
        print("filename: ", csv_filename)
        entry1.configure(state="normal")
        entry1.delete(0,'end')
        entry1.insert(0,csv_filename)
        entry1.configure(state="disabled")

        ##----------- Reads csv file into pandas dataframe -----------##
        df = pd.read_csv(csv_filename, sep=',', low_memory=True)
        print("df:\n",df)
        Header_Row=list(df.columns)
        #print("Header_Row: \n", Header_Row)

        entry2.configure(state="normal")
        entry2.delete(0,'end')
        entry2.insert(0, str(Header_Row))
        entry2.configure(state="disabled")

        ##------------- Inserts new column at index 1 ----------------##
        #count rows and columns
        numRows=df.shape[0]
        numCols=df.shape[1]
        print("numRows: ", numRows)
        print("numCols: ", numCols)
        
        # Determines the first non-header row
        firstRowIndex=0 #what row does the data start on?
        isNumber=False
        for row in range(numRows):
            #print("row:",row)
            for column in range(numCols):
                #print("    column:",column)
                value=df.iloc[row,column]
                try:
                    if pd.isnull(value):
                        raise ValueError('Null Character Found')
                    # float(value)
                    isNumber=True
                    firstRowIndex=row
                    #print("  isaNumber! ", value)
                except:
                    #print("  notaNumber ", value)
                    pass
                if isNumber: break
            if isNumber: break
        print("firstRowIndex: ",firstRowIndex)

        # Determines the timestamp column
        timestampFound=False
        TimestampColumnIndex=0
        for column in range(numCols):
            try:
                #print("column:",column)
                value=df.iloc[firstRowIndex,column]
                if pd.isnull(value): raise ValueError('Null Character Found')
                #print("  value:",value)
                pd.Timestamp(value)
                #print("  Is timestamp!")
                timestampFound=True
                TimestampColumnIndex=column
                break
            except:
                #print("  not Timestamp")
                pass
            if timestampFound:
                break
        if not timestampFound:
            print("no Timestamps found in this file.")
            raise ValueError('No Timestamps Found in this file.')
        print("TimestampColumnIndex:",TimestampColumnIndex)
        
        # saves first timestamp for future calculation
        initialTime=pd.Timestamp(df.iloc[firstRowIndex,TimestampColumnIndex])  
        print("initialTime: ", initialTime)

        TimestampColumnArray = df[Header_Row[TimestampColumnIndex]] # 
        TimeColumnIndex=numCols
        df.insert(TimeColumnIndex,'TimeColumn',TimestampColumnArray)        

        # calculates the time in seconds populated in the TimeColumn
        for row in range(numRows-firstRowIndex):
            nextTime = pd.Timestamp(df.iloc[row+firstRowIndex,TimestampColumnIndex])
            #print("nextTime: ",nextTime)
            df.iloc[row+firstRowIndex,TimeColumnIndex]=(nextTime-initialTime) / pd.Timedelta(seconds=1)

        print("df:\n",df)

        csv_filename_new = csv_filename.strip(".csv")
        csv_filename_new = csv_filename_new+"_time.csv"
        df.to_csv(csv_filename_new, encoding='utf-8', index=False) 
        print(csv_filename_new,"was successfully created!")


def on_closing():
    with open(conf_geometry, "w", encoding='utf-8') as conf:
        conf.write(window.geometry())
    window.destroy()

def read_file():
    pass

    
# initialize tkinter elements
window = tk.Tk()
button1 = ttk.Button(window, text='Batch select csv files', command=select_file)
button2 = ttk.Button(window, text='Read the csv file', command=read_file)
button1.grid(row=0, column=0,padx=2)
button2.grid(row=1, column=0, padx=2)

entry1 = ttk.Entry(window)
entry1.insert(0,'CSV path and filename')
entry1.grid(row=0, column=1, padx=2, pady=5, rowspan=1,columnspan=3,ipadx=200,ipady=4)
entry1.configure(state="disabled")

entry2 = ttk.Entry(window)
entry2.insert(0,'')
entry2.grid(row=1, column=1, padx=2, pady=5, rowspan=1,columnspan=3,ipadx=200,ipady=4)
entry2.configure(state="disabled")

# window attributes
window.protocol("WM_DELETE_WINDOW", on_closing)
window.wm_title("CSV Time Convert Tool")

try:
    with open(conf_geometry, "r", encoding='utf-8') as conf: 
        window.geometry(conf.read())
except OSError:
    window.geometry("500x300")

# run the application
window.mainloop()
