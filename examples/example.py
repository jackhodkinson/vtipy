import time, datetime, os
from vtipy import solartron1260, temperature_controllers, plot_temp

# -------------- Settup --------------------

# define an instance of the solartron controller object
sol = solartron1260()
# Define Frequency Sweep (logscale)
fmin = 0.05 # Errors encountered with Gpib lib for fmin < 0.05! Not sure why...
fmax = 9.8e6
ppd = 20 # points per decade

# define the path to the serial to usb converter connected to the Eurotherm
port_path = '/dev/serial/by-path/' + os.listdir('/dev/serial/by-path')[0]
# check to make sure the path exhists
assert os.path.isdir(port_path) , err_msg['port_path']
# define an instance of the temperature controller object
temp_data_filename = 'temp_data.txt'
tc = temperature_controllers(temp_data_filename,serial_usb_port=port_path)
# set the initial temperature of the Eurotherm

# --------------- Main Program ----------------

tc.ramp_temperature(30)
# Optionally start a live plotting script to display temperature data
# This requires the plot_temp.py file be in the same directory as the main
# script. Comment out the following line if no plotting script is given.
os.system('python plot_temp.py {}'.format(temp_data_filename))
# Thermalise the sample at the initial temperature
# hold_time in minutes
# temp_resolution defines number of temperature measurements per minute
tc.hold( hold_time = 10, temp_resolution = 2)
# initialise the scan number
scan_number = 1
# optionally a label for the scan
# usefull for distinguishing between up and down temperature sweeps

# ------------ Temperature Ramp Loop --------------

scan_label = 'up0' 

# loop through the desired temperature range
for Tset in range(250,320,10):
	# ramp to desired temperature
    tc.ramp_temperature(Tset)
    # thermalise at that temperature
    tc.hold( hold_time = 20, temp_resolution = 2)
    # loop through desired number of impedance scans
    for n in range(3):
    	# get Tcell to include in the metadata of the scan
        Tcell = tc.measure_temperatures()
        # make an impedance measurement
        sol.measure_impedance( scan_number, fmin = fmin, fmax = fmax, ppd = ppd, 
            Tset = Tset, Tcell = Tcell, scan_label = scan_label)
        # incriment the scan number (important so you don't re-write a file!)
        scan_number += 1
        # hold the temperature for some time between each scan
        # make sure it is longer than the time it takes to scan impedance!
    	tc.hold( hold_time = 20, temp_resolution = 2)
