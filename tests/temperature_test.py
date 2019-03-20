import time, datetime, os
# TODO: import os in the example script
# TODO: integrate temp plotting script
# TODO: design command line plotting interface
from vtipy import solartron1260, temperature_controllers

print 'Connecting to solartron\n'
# define an instance of the solartron controller object
sol = solartron1260()
print 'Connection successful\n'
# Define Frequency Sweep (logscale)
fmin = 0.1 # Errors encountered with Gpib lib for fmin < 0.05! Not sure why...
fmax = 9.8e5
ppd = 8 # points per decade

print 'finding port for Eurotherm\n'
# define the path to the serial to usb converter connected to the Eurotherm
# TODO: check if path exhists if not warn
port_path = '/dev/serial/by-path/' + os.listdir('/dev/serial/by-path')[0]
# define an instance of the temperature controller object
print 'found port for Eurotherm\n'
print 'connect to Eurotherm\n'
# TODO: change port_path argument to serial_usb_port
tc = temperature_controllers('temp_data.txt',serial_usb_port=port_path)
print 'connection successful\n'
# set the initial temperature of the Eurotherm
tc.ramp_temperature(30)
# Thermalise the sample at the initial temperature
# hold_time in minutes
# temp_resolution defines number of temperature measurements per minute
print 'making some temperature measurments and holding for one minute\n'
tc.hold(hold_time = 1, temp_resolution = 5)

#print 'finished temperature measurements starting impedance measurements\n'
# initialise the scan number
scan_number = 5

print 'running an impedance sweep\n'
print 'you should see a print statement when the sweep is over\n'
sol.measure_impedance( scan_number, fmin = fmin, fmax = fmax, ppd = ppd, scan_label='10M_1nf')
