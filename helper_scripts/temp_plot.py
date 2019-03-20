import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np
import os
import time
import matplotlib.gridspec as gridspec
import matplotlib.animation as anim

font = {'family' : 'serif',
        'weight' : 'normal',
        'size'   : 18}

plt.rc('font', **font)

fig, ax = plt.subplots(1,1,figsize=(10,5))

def set_axis_params():
    ax.set_xlabel('Time / min')
    ax.set_ylabel('Temperature / $^o$C')
    ax.grid()

set_axis_params()

filename = 'temp_data.txt'
expected_length = 5
refresh_time = 10

def update(i):
    if os.path.exists(filename):
        lines = open(filename).readlines()
        string_array = [line.strip().split(',') for line in lines[1:] if len(line.split(',')) == expected_length]
        float_array = [[float(i) for i in j] for j in string_array]
        data = zip(*float_array)
        ax.clear()
        set_axis_params()
        ax.plot(data[0],data[1],label='Set')
        ax.plot(data[0],data[2],label='Furnace')
        ax.plot(data[0],data[3],label='Cell')
        l = plt.legend()
        plt.pause(refresh_time)
    else:
        time.sleep(refresh_time)
        
a = anim.FuncAnimation(fig,update,frames=None,repeat=False)
plt.show()