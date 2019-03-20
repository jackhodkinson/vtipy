# TODO: Test to see if multiple measurements can be made
# with the solartron object one after another.
import time, datetime, os
# TODO: integrate temp plotting script
# TODO: design command line plotting interface
from vtipy import solartron1260, temperature_controllers, err_msg

# define an instance of the solartron controller object
sol = solartron1260()
# Define Frequency Sweep (logscale)
fmin = 0.1 # Errors encountered with Gpib lib for fmin < 0.05! Not sure why...
fmax = 9.8e5
ppd = 8 # points per decade

# define the path to the serial to usb converter connected to the Eurotherm
port_path = '/dev/serial/by-path/' + os.listdir('/dev/serial/by-path')[0]
# check to make sure the path exhists
# TODO: this assertion error does not seem to work. Check why.
#assert os.path.isdir(port_path) , err_msg['port_path']
# define an instance of the temperature controller object
tc = temperature_controllers('temp_data.txt',serial_usb_port=port_path)

# set the initial temperature of the Eurotherm
#tc.set_temperature(30)
# Thermalise the sample at the initial temperature
# hold_time in minutes
# temp_resolution defines number of temperature measurements per minute
#print 'making some temperature measurments and holding for one minute\n'
#tc.hold(hold_time = 1, temp_resolution = 5)

#print 'finished temperature measurements starting impedance measurements\n'
# initialise the scan number
scan_number = 2

print 'running an impedance sweep\n'
print 'you should see a print statement when the sweep is over\n'
#sol.measure_impedance( scan_number, fmin = fmin, fmax = fmax, ppd = ppd, scan_label='10M_1nf')
sol.measure_impedance( scan_number = scan_number,
	#filename = 'test_{}.txt'.format(scan_number),
	fmin = fmin, fmax = fmax, ppd = ppd, scan_label='scanLabel')
