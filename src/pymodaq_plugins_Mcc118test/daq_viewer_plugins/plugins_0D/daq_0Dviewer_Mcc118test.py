import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter

from daqhats import mcc118, OptionFlags, HatIDs, HatError
from pymodaq_plugins_Mcc118test.hardware.daqhats_utils import select_hat_device, enum_mask_to_string, \
    chan_list_to_mask

class PythonWrapperOfYourInstrument:
    #  TODO Replace this fake class with the import of the real python wrapper of your instrument
    pass

# I don't know where to put that now
channels = [0]
channel_mask = chan_list_to_mask(channels)
num_channels = len(channels)

samples_per_channel = 0

options = OptionFlags.CONTINUOUS

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

    params = comon_parameters+[{'title': 'desired scan rate (Hz)', 'name': 'scan_rate', 'type': 'int', 'value': 1000, 'default': 1000, 'min': 0},]

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
       
        try:
             # Select an MCC 118 HAT device to use.
            address = select_hat_device(HatIDs.MCC_118)
            self.controller: mcc118 = mcc118(address)
        except (HatError, ValueError) as err:
            print('\n', err)
        
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
           actual_scan_rate = self.controller.a_in_scan_actual_rate(num_channels, param)
           self.controller.your_method_to_apply_this_param_change()  # when writing your own plugin replace this line
#        elif ...
        ##

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
        # # Initialize the detector hardware
        # if self.controller is None:
        #     self.board = mcc118(0)  # Initialize MCC118 on address 0
        #     self.controller = self.board
        print('ini detector tried')
        # info = f"Connected to MCC118 - Serial: {self.board.serial()}"
        # self.emit_status(ThreadCommand('update_status', [info]))
        raise NotImplemented  # TODO when writing your own plugin remove this line and modify the one below
        self.ini_detector_init(slave_controller=controller)

        if self.is_master:
            self.controller = PythonWrapperOfYourInstrument()  #instantiate you driver with whatever arguments are needed
            self.controller.open_communication() # call eventual methods

        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        self.dte_signal_temp.emit(DataToExport(name='myplugin',
                                               data=[DataFromPlugins(name='Mock1',
                                                                    data=[np.array([0]), np.array([0])],
                                                                    dim='Data0D',
                                                                    labels=['Mock1', 'label2'])]))

        info = "Whatever info you want to log"
        initialized = self.controller.a_method_or_atttribute_to_check_if_init()  # TODO
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
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
        ## TODO for your custom plugin: you should choose EITHER the synchrone or the asynchrone version following

        total_samples_read = 0
        read_request_size = READ_ALL_AVAILABLE

        # When doing a continuous scan, the timeout value will be ignored in the
        # call to a_in_scan_read because we will be requesting that all available
        # samples (up to the default buffer size) be returned.
        timeout = 5.0

        read_result = self.controller.a_in_scan_read_numpy(read_request_size, timeout)

        y_data = read_result.data  # Single value for 0D viewer
        print(f'sizedata ={y_data.shape()}')
        self.dte_signal.emit(DataToExport(name="DistanceSensor",data=[DataFromPlugins(name="Distance",data=y_data,dim="Data0D",labels=[self.settings["y_label"]])]))


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
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        
        self.controller.__del__()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)
