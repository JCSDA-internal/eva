# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import os
from xarray import Dataset, open_dataset

from eva.data.eva_dataset_base import EvaDatasetBase
from eva.utilities.config import get
from eva.utilities.utils import parse_channel_list

import netCDF4 as nc

# --------------------------------------------------------------------------------------------------


def subset_channels(ds, channels, add_channels_variable=False):

    if 'Channel' in list(ds.dims):

        # Number of user requested channels
        channel_use = len(channels)

        # Number of channels in the file
        channel_in_file = ds.Channel.size

        # If user provided no channels then use all channels
        if channel_use == 0:
            channel_use = channel_in_file

        # Keep needed channels and reset dimension in Dataset
        if channel_use < channel_in_file:
            ds = ds.sel(Channel=channels)

    return ds


# --------------------------------------------------------------------------------------------------


class IodaObsSpace(EvaDatasetBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, dataset_config, data_collections, timing):

        # Get channels for radiances
        # --------------------------
        channels_str_or_list = get(dataset_config, self.logger, 'channels', [])

        # Convert channels to list
        channels = []
        if channels_str_or_list is not []:
            channels = parse_channel_list(channels_str_or_list, self.logger)

        # Filenames to be read into this collection
        # -----------------------------------------
        filenames = get(dataset_config, self.logger, 'filenames')

        # Get missing value threshold
        # ---------------------------
        threshold = float(get(dataset_config, self.logger, 'missing_value_threshold', 1.0e30))

        # Get the groups to be read
        # -------------------------
        groups = get(dataset_config, self.logger, 'groups')

        # Loop over filenames
        # -------------------
        total_loc = 0
        for filename in filenames:
            # Assert that file exists
            if not os.path.exists(filename):
                logger.abort(f'In IodaObsSpace file \'{filename}\' does not exist')

            # Get file header
            ds_header = open_dataset(filename)

            # Fix location in case ioda did not set it
            locations_this_file = range(total_loc, total_loc + ds_header['Location'].size)
            ds_header = ds_header.assign_coords({"Location": locations_this_file})
            total_loc = total_loc + ds_header['Location'].size

            if 'Cluster' in ds_header.keys():
                clusters_this_file = range(0, ds_header['Cluster'].size)
                ds_header = ds_header.assign_coords({"Cluster": clusters_this_file})

            # Read header part of the file to get coordinates
            ds_groups = Dataset()

            # Save sensor_channels for later
            add_channels = False
            if 'Channel' in ds_header.keys():
                sensor_channels = ds_header['Channel']
                add_channels = True

            # Merge in the header and close
            ds_groups = ds_groups.merge(ds_header)
            ds_header.close()

            # Set the channels based on user selection and add channels variable
            ds_groups = subset_channels(ds_groups, channels, True)

            # If groups is empty, read in file to retrieve group list
            groups_present = True
            if not groups:
                groups_present = False
                nc_ds = nc.Dataset(filename)
                groups = list(nc_ds.groups.keys())
                nc_ds.close()

            # Loop over groups
            for group in groups:

                # Group name and variables
                if groups_present:
                    group_name = get(group, self.logger, 'name')
                    group_vars = get(group, self.logger, 'variables', 'all')
                else:
                    group_name = group
                    group_vars = 'all'

                # Set the collection name
                collection_name = dataset_config['name']

                # Read the group
                timing.start(f'IodaObsSpace: open_dataset {os.path.basename(filename)}')
                ds = open_dataset(filename, group=group_name, mask_and_scale=False,
                                  decode_times=False)
                timing.stop(f'IodaObsSpace: open_dataset {os.path.basename(filename)}')

                # If user specifies all variables set to group list
                if group_vars == 'all':
                    group_vars = list(ds.data_vars)

                # Check that all user variables are in the dataset_config
                if not all(v in list(ds.data_vars) for v in group_vars):
                    self.logger.abort('For collection \'' + dataset_config['name'] +
                                      '\', group \'' +
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

                # Reset channel numbers from header and copy channel numbers
                # into MetaData for easier use
                if add_channels:
                    ds['Channel'] = sensor_channels
                    # Explicitly add the channels to the collection (we do not want to
                    # include this in the 'variables' list in the YAML to avoid transforms
                    # being applied to them)
                    ds['MetaData::channelNumber'] = sensor_channels

                # Set channels
                ds = subset_channels(ds, channels)

                # Assert that the collection contains at least one variable
                if not ds.keys():
                    self.logger.abort('Collection \'' + dataset_config['name'] + '\', group \'' +
                                      group_name + '\' in file ' + filename +
                                      ' does not have any variables.')

                # Merge with other groups
                ds_groups = ds_groups.merge(ds)

                # Close dataset_config
                ds.close()

            # Add the dataset_config to the collections
            data_collections.create_or_add_to_collection(collection_name, ds_groups, 'Location')

        # Nan out unphysical values
        data_collections.nan_float_values_outside_threshold(threshold)

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()


    def generate_default_config(self, filenames, collection_name):
        #eva_dict = {'datasets': [{'filenames': filenames,
        #                          'groups': [],
        #                          'missing_value_threshold': 1.0e06,
        #                          'name': collection_name}]}

        eva_dict = {'filenames': filenames,
                    'groups': [],
                    'missing_value_threshold': 1.0e06,
                    'name': collection_name}
        return eva_dict
