from time import sleep
import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter

from daqhats import mcc118, OptionFlags, HatIDs, HatError
from pymodaq_plugins_MCC.hardware.daqhats_utils import select_hat_device, enum_mask_to_string, \
    chan_list_to_mask
# pymodaq_plugins_MCC.
class PythonWrapperOfYourInstrument:
    #  TODO Replace this fake class with the import of the real python wrapper of your instrument
    pass

# I don't know where to put that now
channels = [0]
channel_mask = chan_list_to_mask(channels)
num_channels = len(channels)

samples_per_channel = 0

options = OptionFlags.CONTINUOUS | OptionFlags.DEFAULT #| OptionFlags.NOCALIBRATEDATA

READ_ALL_AVAILABLE = -1


class DAQ_0DViewer_Mcc118test(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    # TODO add your particular attributes here if any

    """

    params = comon_parameters+[
        {'title': 'desired scan rate (Hz)', 'name': 'scan_rate', 'type': 'int', 'value': 1000, 'default': 1000, 'min': 0},
        {'title': 'Calibration Offset (V)', 'name': 'calibration_offset', 'type': 'float', 'value': 0.0, 'default': 0.0},
        {'title': 'Calibration Gain', 'name': 'calibration_gain', 'type': 'float', 'value': 1.0, 'default': 1.0}
    ]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     print('essai init')
    #     try:
    #          # Select an MCC 118 HAT device to use.
    #         address = select_hat_device(HatIDs.MCC_118)
    #         hat = mcc118(address)
    #     except (HatError, ValueError) as err:
    #         print('\n', err)    
        
    def ini_attributes(self):

        self.controller: mcc118 = None

        #TODO declare here attributes you want/need to init with a default value
        pass
        

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        
        if param.name() == "scan_rate":
            scan_rate = param.value()
            if scan_rate > 0 and self.controller:
                self.controller.a_in_scan_actual_rate(num_channels, scan_rate)
                print(f"Scan rate set to {scan_rate} Hz")

        if param.name() in ["calibration_gain", "calibration_offset"] and self.controller:
            try:
                channel = 0  # Assuming channel 0 for calibration
                slope = self.settings['calibration_gain']
                offset = self.settings['calibration_offset']
                self.controller.calibration_coefficient_write(channel, slope, offset)
                print(f"Calibration coefficients set for channel {channel}: Slope={slope}, Offset={offset}")
            except HatError as err:
                print(f"Error setting calibration coefficients: {err}")
        

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        
        print('Initializing detector...')
        self.ini_detector_init(slave_controller=controller)

        try:
            address = select_hat_device(HatIDs.MCC_118)
            self.controller: mcc118 = mcc118(address)
        except (HatError, ValueError) as err:
            print(f"Error initializing MCC 118: {err}")
            return "Initialization failed", False


        # if self.is_master:
        #     self.controller = PythonWrapperOfYourInstrument()  #instantiate you driver with whatever arguments are needed
        #     self.controller.open_communication() # call eventual methods

        try:
             # Select an MCC 118 HAT device to use.
            address = select_hat_device(HatIDs.MCC_118)
            self.controller: mcc118 = mcc118(address)
        except (HatError, ValueError) as err:
            print('\n', err)

        print(self.settings['scan_rate'])
        
        self.controller.a_in_scan_start(channel_mask, samples_per_channel, self.settings['scan_rate'], options)

        try:
            channel = 0  # Assuming channel 0 for initial calibration
            slope = self.settings['calibration_gain']
            offset = self.settings['calibration_offset']
            self.controller.calibration_coefficient_write(channel, slope, offset)
            print(f"Initial calibration coefficients set for channel {channel}: Slope={slope}, Offset={offset}")
        except HatError as err:
            print(f"Error during initial calibration: {err}")

        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        self.dte_signal_temp.emit(DataToExport(name='MCC118test',
                                               data=[DataFromPlugins(name='Mock1',
                                                                    data=[np.array([0]), np.array([0])],
                                                                    dim='Data0D',
                                                                    labels=['Mock1', 'label2'])]))

        info = "mcc118 initialized at address 0"
        initialized = self.controller._initialized
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.controller:
            self.controller.a_in_scan_stop()
            self.controller.a_in_scan_cleanup()
            self.controller.__del__()  
            # self.emit_status(ThreadCommand('Update_Status', ['close comm']))

        #  self.controller.your_method_to_terminate_the_communication()  # when writing your own plugin replace this line

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        if not self.controller:
            print("Controller not initialized")
            return

        # read_request_size = READ_ALL_AVAILABLE
        read_request_size = 1

        # When doing a continuous scan, the timeout value will be ignored in the
        # call to a_in_scan_read because we will be requesting that all available
        # samples (up to the default buffer size) be returned.
        timeout = 5.0

        try:
            read_result = self.controller.a_in_scan_read_numpy(read_request_size, timeout)
        except HatError as err:
            print(f"Error reading data: {err}")
            return

        y_data = read_result.data  # Single value for 0D viewer
        
        self.dte_signal.emit(DataToExport(name="MCC118test",data=[DataFromPlugins(name="Voltage",data=y_data,dim="Data0D",labels=['hello this is a label'])]))
        
        # synchrone version (blocking function)
        #not sure it is synchrone 
        #self.controller.a_in_scan_start(channel_mask, samples_per_channel, scan_rate,options)
        #still need a lot of work
        
        #data_tot = self.controller.your_method_to_start_a_grab_snap()
        #self.dte_signal.emit(DataToExport(name='myplugin',
                                        #   data=[DataFromPlugins(name='Mock1', data=data_tot,
                                        #                         dim='Data0D', labels=['dat0', 'data1'])]))
        #########################################################

        # asynchrone version (non-blocking function with callback)
        # raise NotImplemented  # when writing your own plugin remove this line
        # self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        read_request_size = 1
        timeout = 5.0
        data_tot = self.controller.a_in_scan_read_numpy(read_request_size, timeout)
        self.dte_signal.emit(DataToExport(name='MCC118test',
                                          data=[DataFromPlugins(name='Voltage1', data=data_tot,
                                                                dim='Data0D', labels=['je suis aussi un label'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        
        self.controller.a_in_scan_stop()
        self.controller.a_in_scan_cleanup()
        self.emit_status(ThreadCommand('Update_Status', ['close comm']))
        return ''


if __name__ == '__main__':
    main(__file__)
