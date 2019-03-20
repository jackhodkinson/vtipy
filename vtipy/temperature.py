"""
This module is designed to control the temperature controllers used in the
variable temperature impedance control system.

"""
import serial
import minimalmodbus
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
import time
import datetime
import os



class temperature_controllers(minimalmodbus.Instrument, MAX31855.MAX31855):
    """
    This class controls both the MAX31855 temperature controller
    and the Eurotherm 3216.

    Methods are defined to allow measurement and recording of the temperature
    from the Eurotherm and the MAX31855 as well as to change the setpoint 
    tempreature of the Eurotherm controller.
    
    This control is accomplished by inheritance from the
    minimalmodbus.Instrument and MAX31855.MAX31855 classes.

    Parameters
    ----------
    filename : string
        The name assigned to the file in which temperature measurements will be
        recorded.
    serial_usb_port : string
        The path associated with the serial-to-USB converter on the Raspberry Pi
        filesystem.
    addr : int, optional
        The slave address of the serial-to-USB converter (connected to the
        Eurotherm controller).
    CLK : int, optional
        I/O port on the Raspberry Pi associated with the clock pin on the
        MAX31855.
    CS : int, optional
        I/O port on the Raspberry Pi associated with the "chip sellect" port
        on the MAX31855.
    DO : int, optional
        I/O port on the Raspberry Pi associated with the "data out" port on the
        MAX31855.

    Example
    -------
    The following is an example of how to initialise the temeprature controller
    object, make an initial temperature measurement, ramp the temperature,
    and hold the temperature at a desired setpoint.

    >>> from vtipy import temperature_controllers
    >>> tc = temperature_controllers("temp.txt", serial_usb_port)
    >>> Tcell = tc.measure_temperatures()
    >>> tc.ramp_temperature( Tset = 100 )
    >>> tc.hold( hold_time = 60)

    """

    def __init__( self, filename, serial_usb_port,
        addr=1, CLK = 25, CS  = 24, DO  = 18):
        try:
            minimalmodbus.Instrument.__init__(self, serial_usb_port,
                slaveaddress=addr)
        except:
            print 'make sure the eurotherm is plugged in'
        self.serial.baudrate = 9600
        self.serial.timeout = 1.0
        MAX31855.MAX31855.__init__(self, clk = 25, cs  = 24, do  = 18)
        self.t0 = None
        self.filename = filename
        with open(self.filename,'w') as f:
            f.write('datetime, Tset, Teuro, Tcell, Tinternal \n')
        

    def read_setpoint(self):
        """
        Reads the setpoint temperature from the Eurotherm. This is read from
        register 5 of the Eurotherm 3216. This might need to be adapted for
        other Eurotherm controllers. See the Eurotherm manual.
        
        Returns
        -------
        setpoint (string?):
            The setpoint temperature from the Eurotherm as a string.

        """
        setpoint = self.read_register(5)
        return setpoint

    def set_setpoint(self,Tset):
        """
        Sets the setpoint temperature of the Eurotherm. This is accomplished by
        setting register 24 of the Eurotherm 3216. This might need to be
        adapted for other Eurotherm controllers. See the Eurotherm manual.

        Parameters
        ----------
        Tset : int
            The new setpoint temperature (in degrees Celsius) 
            for the Eurotherm controller.

        """
        self.write_register(24,Tset)

    def read_process_temperature(self):
        """ Returns the  furnace temperature from the Eurotherm """
        return self.read_register(1)

    def measure_temperatures(self):
        """
        This method serves two purposes: Firstly, it measures the two cell and
        furnace temperature. Secondly, this method records time since the
        initial temperature measurement (dt), the setpoint temperature from
        the Eurotherm.

        The measurement is recorded into the temperature datafile specified
        when an instance of this class is defined. The data is added to the
        file as a comma separated line of the format:

            " dt, Tsetpoint, Teuro, Tcell, Ttc_internal "

        Returns
        -------
        Tcell : string

        """
        if self.t0 is None:
            self.t0 = time.time()
        dt = (time.time()-self.t0)/60.
        Tsetpoint = self.read_setpoint()
        Teuro = self.read_process_temperature()
        Tcell = self.readTempC()
        Ttc_internal = self.readInternalC()
        with open(self.filename,'a') as f:
            f.write(
                '{0:0.2F}, {1:0.2F}, {2:0.2F}, {3:0.2F}, {4:0.2F} \n'.format(
                datetime.datetime.now(), Tsetpoint, Teuro, Tcell, Ttc_internal)
                )
        return Tcell

    def ramp_temperature(self, Tset, ramp_time = 1):
        """
        Parameters
        ----------
        Tset : int
            Setpoint temperature in degrees C.
        ramp_time : int
            Time (in min) per degree C.

        """
        'ramp time is: minutes per degree C'
        print 'ramping to ' + str(Tset)
        T0 = self.read_process_temperature()
        DT = int(Tset) - int(T0)
        if DT > 0:
            for T in range(int(T0) + 1, int(Tset)+1):
                print 'stepping to '+str(T)
                self.measure_temperatures()
                self.set_setpoint(T)
                for i in range(6):
                    self.measure_temperatures()
                    time.sleep(10*ramp_time)
        else:
            print 'Tset is less than process temperature'
            print 'Moving Tset to '+str(Tset)
            self.measure_temperatures()
            self.set_setpoint(Tset)

    def hold(self, hold_time, temp_resolution = 2):
            """
                This function holds the setpoint temperature of the Eurotherm
                while measuring and recording the process temperatures at the 
                specified temperature resolution.

                Parameters
                ----------
                hold_time : int
                    Time in minutes to hold the Eurotherm setpoint.
                temp_resolution : int
                    Temperature measurements per minute.
                
            """
            assert isinstance(hold_time,int), "hold_time needs to be an int"
            assert isinstance(
                temp_resolution,int), "temp_resolution needs to be an int"
            
            cellT = self.measure_temperatures()
            for _ in range(hold_time*temp_resolution):
                cellT = self.measure_temperatures()
                time.sleep(1. / temp_resolution * 60)