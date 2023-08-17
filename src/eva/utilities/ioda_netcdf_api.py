# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


def read_ioda_variable(fh, group, variable, channel=None):

    """
    Read an IODA variable from a specified group and channel (if applicable).

    Args:
        fh: The IODA file handle.
        group (str): The IODA group from which to read the variable.
        variable (str): The variable to be read.
        channel (int or None): The channel number for the variable if applicable. Default is None.

    Returns:
        ndarray: The data read from the IODA variable.
    """

    # Set the variables to be read
    # ----------------------------
    if group == 'omb':
        var1 = 'ObsValue'
        var2 = 'hofx'
    elif group == 'Gsiomb':
        var1 = 'ObsValue'
        var2 = 'GsiHofX'
    elif group == 'GsiombBc':
        var1 = 'ObsValue'
        var2 = 'GsiHofXBc'
    else:
        var1 = group
        var2 = None

    # Read the data
    # -------------
    if channel is None:

        data = fh.groups[var1].variables[variable][:]

        if var2 is not None:
            data -= fh.groups[var2].variables[variable][:]

    else:

        data = fh.groups[var1].variables[variable][:, channel-1]

        if var2 is not None:
            data -= fh.groups[var2].variables[variable][:, channel-1]

    return data


# --------------------------------------------------------------------------------------------------
