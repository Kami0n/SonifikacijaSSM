import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd

import mido
import time
import requests
from datadog import statsd

from tonal import Tonal, mapping

import traceback

output = mido.open_output()
tonal = Tonal()
mid_range = tonal.create_sorted_midi("Chromatic", "C")
start = time.time()
max_time = 100

inputData = pd.read_csv("data.csv", header=0)
inputData = inputData.set_index('LETO')
temps = inputData.values.flatten().tolist()


for value in temps:
    try:
        output.send(mido.Message( 'note_on', note = mapping(value, 0, 30), velocity=80, channel=0))
        print( value, "note on", 1)
        
        time.sleep(0.2)
        
        output.send(mido.Message( 'note_off', note = mapping(value, 0, 30), channel=0))
        print( value, "note off", 1)
        
    except:
        # printing stack trace 
        traceback.print_exc() 
        
