import os
import Gpib, time
import numpy as np, sys, datetime
from multiprocessing import Process



class solartron1260(Gpib.Gpib):
    """

    Parameters
    ----------
    Vac : float, optional
        A.C. voltage for impedance measurements.
    Vdc : float, optional
        D.C. bias.
    integration_time: int, optional
        Integration time in seconds.  
    gpib_address : int, optional,
        Gpib address of the instrument. Default is 2.        

    Example
    -------
    Here is a demonstration of how the object is initialised
    and how a frequency dependent measurement is executed.

    >>> from vtipy import solartron1260
    >>> sol = solartron1260()
    >>> sol.measure_impedance( scan_number = 1 )

    """

    def __init__(self, Vac=0.5, Vdc=0.0,
        integration_time = 1, gpib_address = 2):
        """
        The initialisation of the solartron1260 object.

        The object inherits from the Gpib.Gpib class defined in the python
        module of the Linux_Gpib library.

        Parameters
        ----------
        Vac : float, optional
            A.C. voltage for impedance measurements.
        Vdc : float, optional
            D.C. bias.
        integration_time: int, optional
            Integration time in seconds.
        gpib_address : int, optional,
            Gpib address of the instrument. Default is 2.            

        """
            
        Gpib.Gpib.__init__(self,name=0, pad=gpib_address)
        
        self.write('TT2')
        time.sleep(3)

        command_list = ['OS 0','OT 0',"OP 2,1",'CZ 1', 'UW 1',
                         'IP 1,1', 'OU 1,0','IP 2,1', 'OU 2,0',
                          'VB '+str(Vdc), 'VA '+str(Vac), 'DC 1,0',
                           'DC 3,0','RA 1,0', 'IS '+str(integration_time)]

        for n,command in enumerate(command_list):
            self.write(command)
            time.sleep(0.02)


            
            
    def send(self,msg):
        """
        Sends a message to the solartron. Just like the Gpib.Gpib.write except
        a 0.02 s sleep time is applied to prevent too many signals being sent
        at the same time.

        Parameters
        ----------
        msg : string
            The message to send the solartron. This should be one
            of the instructions from the instruction set found in the
            solartron manual.

        Returns
        -------
            None

         """
        self.write(msg)
        time.sleep(0.02)


    def measure_frequency(self,frequency):
        """
        Sends an instruction to the Solarton to measures impedance
        at the specified frequency.
        
        Parameters
        ----------
        frequency : float
            frequency for measurement.

        Returns
        -------
        result : string
            Impedance data formatted as a comma separated
            string. The first three values (frequency, magnitude, and the
            argument) are the important values that need to be saved.

        
        """
        fm = "{:.1E}".format(frequency)
        self.send('FR ' + fm)     # Set generator frequency
        self.send("SI")
        if frequency < 0.1:
            time.sleep(1./frequency+2)
        # Set Display source to 'Z1=V1/I'
        # to convert last measurement to Z, theta    
        self.send('SO 1,3')
        self.send('DO')
        time.sleep(0.05)
        result = self.read(43).strip()
        return result

    def measure_impedance_process(
        self, scan_number, filename,
        fmin, fmax, ppd, 
        Tset, Tcell, scan_label
        ):
        """
        Instructs the Solartron to measure the impedance over a range of
        frequencies.

        This method is designed to be run in parallel with a main script as to
        allow the main script to continue to monitor process temperatures
        while the impedance is measured. This is accomplished by using the
        solartron1260.measure_impedance method which calls this method (the 
        solartron1260.measure_impedance_process) as a sub-process. However,
        this method may be run independently if no other measurements are
        required to be run in parallel.

        The parameters of the method are the same as those detailed in the
        solartron1260.measure_impedance method, however, the default values
        set for that method are not set here. They all must be provided
        explicitly.

        Parameters
        ----------
        scan_number : int
            This should be specified as to indicate the relative order of the
            measurement.
        filename: None, string
            The name of file in which impedance data will be
            stored. If set as None it will be assigned a name based on the
            scan number: "scan_n.txt", where n = scan_number.
        fmin : float
            The minimum frequency (in Hz) of the impedance sweep.
            Cation should be taken when setting this value to anything less
            than 0.05 Hz as errors with the Gpib.Gpib library are encountered.
        fmax : float
            The maximum frequency (in Hz) of the impedance sweep. Max value is
            1e7.
        ppd : int
            The number of points per decade at which an impedance measurement
            will be recorded.
        Tset : int
            The setpoint temperature from the Eurotherm. The value is stored
            in the header of the datafile.
        Tcell : int
            The "cell temperature" as measured by the MAX31855 thermocouple.
            The value is stored in the header of the datafile.
        scan_label : string
            A label to provide extra meta-data for later analysis.
            Typically this is set to "up" or "down" to distinguish measurements
            during an upward or downward temperature sweep. This value is
            recorded in the header of the datafile. 

        """
        
        print 'measuring impedance' # debugging
        
        # By default the filename is None but can optionally be set.
        if not filename:
            filename = "scan_{}.txt".format(scan_number)
        if not os.path.isdir('scans'):
            os.makedirs('./scans')
        file_path = './scans/'+filename

        
        # write the scan header
        now = datetime.datetime.now()
        with open(file_path,'w') as f:
            f.write('scanNo, date, startTime, cellT, setT, scan_label\n')
            f.write( '{}, {}, {}, {}, {}, {}\n'.format( 
                scan_number, now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"), Tcell, Tset, scan_label)
                )

        print 'scan file header has been written' # debugging

        # calculate frange and run frequency sweep
        numpoints = int(ppd*(np.log10(fmax)-np.log10(fmin)))
        frange = np.logspace(*np.log10((fmin,fmax)),num = numpoints)
        frange = frange[::-1]
        
        print 'beginning frequency sweep\n' # debugging
        for f in frange:
            try:
                result = self.measure_frequency(f)
            except:
                result = self.measure_frequency(1.)
                result = self.measure_frequency(f)
            result = ','.join(result.split(',')[:4])
            with open(file_path,'a') as f:
                f.write(result + '\n')
        print 'finished impedance sweep\n'

    # TODO: check fmin > fmax
    # TODO: check ppd is an int ?
    def measure_impedance(
        self,scan_number,filename=None,
        fmin=0.05, fmax=9.8e6, ppd=20, 
        Tset=None,Tcell=None,scan_label=None
        ):
        """

        Sends an instructions to the Solartron to make an impedance measurement
        over a range of frequencies. This is accomplished by executing the
        solartron1260.measure_impedance_process method as a subprocess as to
        allow a main control script to continue to monitor temperature while
        this runs in parallel.

        Parameters
        ----------
        scan_number : int, optional
            This should be specified as to indicate the relative order of the
            measurement.
        filename: None, string
            The name of file in which impedance data will be
            stored. If left as None it will be assigned a name based on the
            scan number: "scan_n.txt", where n = scan_number.
        fmin : float, optional
            The minimum frequency of the impedance sweep. The default value
            is 0.05.
        fmax : float, optional
            The maximum frequency of the impedance sweep. The default value
            is 9.8e6.
        ppd : int, optional
            The number of points per decade at which an impedance measurement
            will be recorded. Default is 20.
        Tset : None, int
            The setpoint temperature from the Eurotherm. If set
            it is stored in the header of the datafile. It should be set
            during variable temperature experiments. If left as none a NAN
            value will be recorded in the header.
        Tcell : None, int
            The "cell temperature" as measured by the MAX31855 thermocouple.
            If set it is stored in the header of the datafile. If left as none
            a NAN value will be recorded in the header.
        scan_label : None, string
            Optional label to provide extra meta-data for later analysis.
            Typically this is set to "up" or "down" to distinguish measurements
            during an upward or downward temperature sweep. This value is
            recorded in the header of the datafile. 

        """
        Process(
            target = self.measure_impedance_process,
            args=(
                scan_number, filename,
                fmin, fmax, ppd, 
                Tset,Tcell,scan_label
                )
            ).start()
        
