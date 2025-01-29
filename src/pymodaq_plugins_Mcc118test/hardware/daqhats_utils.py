"""
    This file contains helper functions for the MCC DAQ HAT Python examples.
"""
from __future__ import print_function
from daqhats import hat_list, HatError


def select_hat_device(filter_by_id):
    # type: (HatIDs) -> int # type: ignore
    """
    This function performs a query of available DAQ HAT devices and determines
    the address of a single DAQ HAT device to be used in an example.  If a
    single HAT device is present, the address for that device is automatically
    selected, otherwise the user is prompted to select an address from a list
    of displayed devices.

    Args:
        filter_by_id (int): If this is :py:const:`HatIDs.ANY` return all DAQ
            HATs found.  Otherwise, return only DAQ HATs with ID matching this
            value.

    Returns:
        int: The address of the selected device.

    Raises:
        Exception: No HAT devices are found or an invalid address was selected.

    """
    selected_hat_address = None

    # Get descriptors for all of the available HAT devices.
    hats = hat_list(filter_by_id=filter_by_id)
    number_of_hats = len(hats)

    # Verify at least one HAT device is detected.
    if number_of_hats < 1:
        raise HatError(0, 'Error: No HAT devices found')
    elif number_of_hats == 1:
        selected_hat_address = hats[0].address
    else:
        # Display available HAT devices for selection.
        for hat in hats:
            print('Address ', hat.address, ': ', hat.product_name, sep='')
        print('')

        address = int(input('Select the address of the HAT device to use: '))

        # Verify the selected address if valid.
        for hat in hats:
            if address == hat.address:
                selected_hat_address = address
                break

    if selected_hat_address is None:
        raise ValueError('Error: Invalid HAT selection')

    return selected_hat_address


def enum_mask_to_string(enum_type, bit_mask):
    # type: (Enum, int) -> str # type: ignore
    """
    This function converts a mask of values defined by an IntEnum class to a
    comma separated string of names corresponding to the IntEnum names of the
    values included in a bit mask.

    Args:
        enum_type (Enum): The IntEnum class from which the mask was created.
        bit_mask (int): A bit mask of values defined by the enum_type class.

    Returns:
        str: A comma separated string of names corresponding to the IntEnum
        names of the values included in the mask

    """
    item_names = []
    if bit_mask == 0:
        item_names.append('DEFAULT')
    for item in enum_type:
        if item & bit_mask:
            item_names.append(item.name)
    return ', '.join(item_names)


def chan_list_to_mask(chan_list):
    # type: (list[int]) -> int
    """
    This function returns an integer representing a channel mask to be used
    with the MCC daqhats library with all bit positions defined in the
    provided list of channels to a logic 1 and all other bit positions set
    to a logic 0.

    Args:
        chan_list (int): A list of channel numbers.

    Returns:
        int: A channel mask of all channels defined in chan_list.

    """
    chan_mask = 0

    for chan in chan_list:
        chan_mask |= 0x01 << chan

    return chan_mask


def validate_channels(channel_set, number_of_channels):
    # type: (set, int) -> None
    """
    Raises a ValueError exception if a channel number in the set of
    channels is not in the range of available channels.

    Args:
        channel_set (set): A set of channel numbers.
        number_of_channels (int): The number of available channels.

    Returns:
        None

    Raises:
        ValueError: If there is an invalid channel specified.

    """
    valid_chans = range(number_of_channels)
    if not channel_set.issubset(valid_chans):
        raise ValueError('Error: Invalid channel selected - must be '
                         '{} - {}'.format(min(valid_chans), max(valid_chans)))


def read_data(hat, num_channels):
    """
    Reads data from the specified channels on the specified DAQ HAT devices
    and updates the data on the terminal display.  The reads are executed in a
    loop that continues until the user stops the scan or an overrun error is
    detected.

    Args:
        hat (mcc118): The mcc118 HAT device object.
        num_channels (int): The number of channels to display.

    Returns:
        None

    """
    total_samples_read = 0
    read_request_size = READ_ALL_AVAILABLE

    # When doing a continuous scan, the timeout value will be ignored in the
    # call to a_in_scan_read because we will be requesting that all available
    # samples (up to the default buffer size) be returned.
    timeout = 5.0

    # Read all of the available samples (up to the size of the read_buffer which
    # is specified by the user_buffer_size).  Since the read_request_size is set
    # to -1 (READ_ALL_AVAILABLE), this function returns immediately with
    # whatever samples are available (up to user_buffer_size) and the timeout
    # parameter is ignored.
    while True:
        read_result = hat.a_in_scan_read(read_request_size, timeout)

        # Check for an overrun error
        if read_result.hardware_overrun:
            print('\n\nHardware overrun\n')
            break
        elif read_result.buffer_overrun:
            print('\n\nBuffer overrun\n')
            break

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        total_samples_read += samples_read_per_channel

        y_data = np.array([current_distance])  # Single value for 0D viewer

        self.dte_signal.emit(DataToExport(name="DistanceSensor",data=[DataFromPlugins(name="Distance",data=y_data,dim="Data0D",labels=[self.settings["y_label"]])]))

        # # Display the last sample for each channel.
        # print('\r{:12}'.format(samples_read_per_channel),
        #       ' {:12} '.format(total_samples_read), end='')

        # if samples_read_per_channel > 0:
        #     index = samples_read_per_channel * num_channels - num_channels

        #     for i in range(num_channels):
        #         print('{:10.5f}'.format(read_result.data[index+i]), 'V ',
        #               end='')
        #     stdout.flush()

        #     sleep(0.1)

    print('\n')



