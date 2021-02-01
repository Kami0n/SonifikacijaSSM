"""
GUI -> vnos datoteke -> sonifikacija podatkov

-> povezava med podatki in zvokom (intenziteta?)
-> gibanje, žiroskopi
-> srčni utrip (kaj se zgodi ko je vrednost nenatančna, šum, tišina, pisk?)

-> filtriranje vhodnih podatkov (lowpass!)

"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from os import listdir
from os.path import isfile, join

clear = lambda: os.system('cls')
clear()

import queue
import threading
import time
import traceback
import numpy as np
import pandas as pd

import mido
from tonal import Tonal, mapping

import PySimpleGUI as sg

from tkinter import *
from random import randint

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as Tk

import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
stop_threads = False

def sonifyFile(temps, gui_queue):
    global stop_threads 
    output = mido.open_output()
    
    tonal = Tonal()
    #mid_range = tonal.create_sorted_midi("Chromatic", "C")
    #start = time.time()
    #max_time = 100
    
    minimal = min(temps)
    maximal = max(temps)
    print(minimal)
    print(maximal)
    
    for value in temps:
        try:
            output.send(mido.Message( 'note_on', note = mapping(value, minimal, maximal), velocity=80, channel=0))
            print( "note on", value )
            time.sleep(0.05) # 50ms je razdalja med vzorci pri kolesarjenju (vzorci so decimirani!)
            output.send(mido.Message( 'note_off', note = mapping(value, minimal, maximal), channel=0))
            print( "note off", value )
            
            if stop_threads: 
                break
        except:
            # printing stack trace 
            traceback.print_exc()

 ######   ##     ## ####
##    ##  ##     ##  ##
##        ##     ##  ##
##   #### ##     ##  ##
##    ##  ##     ##  ##
##    ##  ##     ##  ##
 ######    #######  ####

def the_gui():
    global stop_threads
    gui_queue = queue.Queue()  # queue used to communicate between the gui and the threads

    textsize = 10
    btnsize = 10
    textWidth = 100
    layout = [
                [sg.Text('Select file with data:'), sg.Input(), sg.FileBrowse() ],
                [sg.Text('Select column'), sg.Input(key="-col-")],
                [sg.Button('Play data!', key='Load'), sg.Button('Stop playing!', key='STOP')],
                [sg.Canvas(size=(640, 480), key='canvas')],
            ]

    window = sg.Window('CSV Data Sonification').Layout(layout)
    window.Finalize()
    
    fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
    
    figure_canvas_agg = FigureCanvasTkAgg(fig, window["canvas"].TKCanvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    
    # --------------------- EVENT LOOP ---------------------
    while True:
        event, values = window.Read(timeout=100)       # wait for up to 100 ms for a GUI event
        
        if event is None or event == 'Exit':
            break
        elif(event == 'STOP'):
            stop_threads = True
            fig.clf() # clear figure
            
        elif(event == 'Load'):
            stop_threads = False
            inputData = pd.read_csv(values[0], header=0, index_col=0)
            print(inputData)
            
            columnId = values['-col-']
            if(columnId.isnumeric() and len(inputData.columns) < int(columnId) ):
                columnId = int(values['-col-'])
            else:
                columnId = 0
            
            temps = inputData[inputData.columns[columnId]].tolist()
            
            fig.clf() # clear figure
            fig.add_subplot(111).plot(inputData)
            figure_canvas_agg.draw()
            
            try:
                threading.Thread(target=sonifyFile, args=( temps, gui_queue, ), daemon=True).start()
            except Exception as e:
                print('Error starting work thread. Did you input a valid # of seconds? You entered: %s' % values['_SECONDS_'])
        
        # --------------- Check for incoming messages from threads  ---------------
        try:
            message = gui_queue.get_nowait()
        except queue.Empty:             # get_nowait() will get exception when Queue is empty
            message = None              # break from the loop if no more messages are queued up
        
        # if message received from queue, display the message in the Window
        if message:
            #print('Got a message back from the thread: ', message)
            window.Element('text3').Update(value = message )
            window.Refresh()
            
    # if user exits the window, then close the window and exit the GUI func
    window.Close()


##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##

if __name__ == '__main__':
    the_gui()
    print('Exiting Program')