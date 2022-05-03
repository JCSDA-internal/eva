# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import xarray as xr

from eva.eva_base import EvaBase
from eva.utilities.config import get
from eva.utilities.utils import parse_channel_list


# --------------------------------------------------------------------------------------------------


def subset_channels(ds, channels, add_channels_variable=False):

    if 'nchans' in list(ds.dims):

        # Number of user requested channels
        nchan_use = len(channels)

        # Number of channels in the file
        nchan_in_file = ds.nchans.size

        # If user provided no channels then use all channels
        if nchan_use == 0:
            nchan_use = nchan_in_file

        # Keep needed channels and reset dimension in Dataset
        if nchan_use < nchan_in_file:
            ds = ds.sel(nchans=channels)

    return ds

# --------------------------------------------------------------------------------------------------


class IodaObsSpace(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, data_collections):

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

            # Get the groups to be read
            # -------------------------
            groups = get(dataset, self.logger, 'groups')

            # Loop over filenames
            # -------------------
            for filename in filenames:

                # Get file header
                ds_header = xr.open_dataset(filename)

                # Read header part of the file to get coordinates
                ds_groups = xr.Dataset()

                # Merge in the header and close
                ds_groups = ds_groups.merge(ds_header)
                ds_header.close()

                # Set the channels based on user selection and add channels variable
                ds_groups = subset_channels(ds_groups, channels, True)

                # Loop over groups
                for group in groups:

                    # Group name and variables
                    group_name = get(group, self.logger, 'name')
                    group_vars = get(group, self.logger, 'variables')

                    # Set the collection name
                    collection_name = dataset['name']

                    # Read the group
                    ds = xr.open_dataset(filename, group=group_name)

                    # Check that all user variables are in the dataset
                    if not all(v in list(ds.keys()) for v in group_vars):
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

                    # Set channels
                    ds = subset_channels(ds, channels)

                    # Assert that the collection contains at least one variable
                    if not ds.keys():
                        self.logger.abort('Collection \'' + dataset['name'] + '\', group \'' +
                                          group_name + '\' in file ' + filename +
                                          ' does not have any variables.')

                    # Merge with other groups
                    ds_groups = ds_groups.merge(ds)

                    # Close dataset
                    ds.close()

                # Add the dataset to the collections
                data_collections.create_or_add_to_collection(collection_name, ds_groups, 'nlocs')

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()
