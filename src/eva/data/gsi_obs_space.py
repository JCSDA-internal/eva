# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------
import os
import numpy as np
from itertools import groupby
from xarray import Dataset, open_dataset

from eva.eva_base import EvaBase
from eva.utilities.config import get
from eva.utilities.utils import parse_channel_list


# --------------------------------------------------------------------------------------------------


def all_equal(iterable):
    """
    Checks to see if array is all the same. Returns True
    if they are else returns False.
    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


# --------------------------------------------------------------------------------------------------


def uv(group_vars):
    """
    Adds 'uv' suffix to beginning of specified variables
    if they are included in input list of vars
    """
    change_vars = ['Obs_Minus_Forecast_adjusted',
                   'Obs_Minus_Forecast_unadjusted',
                   'Observation']

    # Find if change variables are in group_vars
    good_vars = [x for x in change_vars if x in group_vars]

    # Loop through existing variables, add u_ and v_ versions
    for var in good_vars:
        group_vars.append('u_' + var)
        group_vars.append('v_' + var)

    # Drop existing variables without u/v suffix
    group_vars = list(set(group_vars) - set(good_vars))

    return group_vars


# --------------------------------------------------------------------------------------------------


def subset_channels(ds, channels, logger, add_channels_variable=False):

    if 'nchans' in list(ds.dims):

        # Number of user requested channels
        nchan_use = len(channels)

        # Number of channels in the file
        nchan_in_file = ds.nchans.size

        if nchan_use == 0:
            nchan_use = nchan_in_file

        if all(x in ds['sensor_chan'] for x in channels):
            ds = ds.sel(nchans=channels)

        else:
            bad_chans = [x for x in channels if x not in ds['sensor_chan']]

            logger.abort(f"{', '.join(str(i) for i in bad_chans)} was inputted as a channel " +
                         "but is not a valid entry. Valid channels include: \n" +
                         f"{', '.join(str(i) for i in ds['sensor_chan'].data)}")

    return ds


# --------------------------------------------------------------------------------------------------


def satellite_dataset(ds):
    """
    Builds a new dataset to reshape satellite
    data.
    """
    nchans = ds.dims['nchans']
    iters = int(ds.dims['nobs']/nchans)

    coords = {
        'nchans': (('nchans'), ds['sensor_chan'].data),
        'nobs': (('nobs'), np.arange(0, iters)),
        'BC_angord_arr_dim': (('BC_angord_arr_dim'), np.arange(0, 4))
    }

    data_vars = {}
    # Loop through each variable
    for var in ds.variables:

        # If variable has len of nchans, pass along data
        if len(ds[var]) == nchans:
            data_vars[var] = (('nchans'), ds[var].data)

        # If variable is BC_angord, reshape data
        elif var == 'BC_angord':
            data = np.reshape(ds['BC_angord'].data,
                              (iters, nchans, ds.dims['BC_angord_arr_dim']))
            data_vars[var] = (('nobs', 'nchans', 'BC_angord_arr_dim'), data)

        # Deals with how to handle nobs data
        else:
            # Check if values repeat over nchans
            condition = all_equal(ds[var].data[0:nchans])

            # If values are repeating over nchan iterations, keep as nobs
            if condition:
                data = ds[var].data[0::nchans]
                data_vars[var] = (('nobs'), data)

            # Else, reshape to be a 2d array
            else:
                data = np.reshape(ds[var].data, (iters, nchans))
                data_vars[var] = (('nobs', 'nchans'), data)

    # create dataset
    new_ds = Dataset(data_vars=data_vars,
                     coords=coords,
                     attrs=ds.attrs)

    return new_ds


# --------------------------------------------------------------------------------------------------


class GsiObsSpace(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, data_collections, timeing):

        # Loop over the datasets
        # ----------------------
        for dataset in self.config.get('datasets'):

            # Get channels for radiances
            # --------------------------
            channels_str_or_list = get(dataset, self.logger, 'channels', [])

            # Convert channels to list
            channels = []
            if channels_str_or_list is not []:
                channels = parse_channel_list(channels_str_or_list, self.logger)

            # Filenames to be read into this collection
            # -----------------------------------------
            filenames = get(dataset, self.logger, 'filenames')

            # File variable type
            if 'satellite' in dataset:
                satellite = get(dataset, self.logger, 'satellite')
                sensor = get(dataset, self.logger, 'sensor')
            else:
                variable = get(dataset, self.logger, 'variable')

            # Get missing value threshold
            # ---------------------------
            threshold = float(get(dataset, self.logger, 'missing_value_threshold', 1.0e30))

            # Get the groups to be read
            # -------------------------
            groups = get(dataset, self.logger, 'groups')

            # Loop over filenames
            # -------------------
            for filename in filenames:

                # Loop over groups
                for group in groups:

                    # Group name and variables
                    group_name = get(group, self.logger, 'name')
                    group_vars = get(group, self.logger, 'variables', 'all')

                    # Set the collection name
                    collection_name = dataset['name']

                    ds = open_dataset(filename, mask_and_scale=False,
                                      decode_times=False)

                    # If user specifies all variables set to group list
                    if group_vars == 'all':
                        group_vars = list(ds.data_vars)

                    # Reshape variables if satellite diag
                    nchans_present = False
                    if 'nchans' in ds.dims:
                        ds = satellite_dataset(ds)
                        ds = subset_channels(ds, channels, self.logger)

                    # Adjust variable names if uv
                    if 'variable' in locals():
                        if variable == 'uv':
                            group_vars = uv(group_vars)

                    # Check that all user variables are in the dataset
                    if not all(v in list(ds.data_vars) for v in group_vars):
                        self.logger.abort('For collection \'' + dataset['name'] + '\', group \'' +
                                          group_name + '\' in file ' + filename +
                                          f' . Variables {group_vars} not all present in ' +
                                          f'the data set variables: {list(ds.keys())}')

                    # Drop data variables not in user requested variables
                    vars_to_remove = list(set(list(ds.keys())) - set(group_vars))
                    ds = ds.drop_vars(vars_to_remove)

                    # Rename variables with group
                    rename_dict = {}
                    for group_var in group_vars:
                        rename_dict[group_var] = group_name + '::' + group_var
                    ds = ds.rename(rename_dict)

                    # Assert that the collection contains at least one variable
                    if not ds.keys():
                        self.logger.abort('Collection \'' + dataset['name'] + '\', group \'' +
                                          group_name + '\' in file ' + filename +
                                          ' does not have any variables.')

                # Add the dataset to the collections
                data_collections.create_or_add_to_collection(collection_name, ds, 'nobs')

        # Nan out unphysical values
        data_collections.nan_float_values_outside_threshold(threshold)

        # Change the channel dimension name
        data_collections.adjust_channel_dimension_name('nchans')

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()
