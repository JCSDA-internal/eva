# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


def read_ioda_variable(fh, group, variable, channel=None):

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
