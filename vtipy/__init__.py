from impedance import solartron1260
from temperature import temperature_controllers

err_msg = {
	'port_path':
		"""
		Port_path was not found.
		Make sure the Eurotherm is plugged into the Pi correctly.
		Make sure the path to the USB-Serial adaptor is specified correctly.
		"""
}