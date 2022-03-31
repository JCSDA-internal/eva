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


class IodaObsSpace(EvaBase):

    def execute(self, data_collections):

        # Local copies
        logger = self.logger
        config = self.config

        # Get the list of datasets to create
        datasets = config.get('datasets')

        # Loop over the datasets
        for dataset in datasets:

            # Get the groups to be read
            groups = get(dataset, logger, 'groups')

            # Get variables
            variables = get(dataset, logger, 'variables')

            # Get channels
            channels_str_or_list = get(dataset, logger, 'channels', [])

            # Convert channels to list
            if channels_str_or_list is not []:
                channels = parse_channel_list(channels_str_or_list, logger)

            # Set number of channels
            nchan = len(channels)

            # Get metadata
            metadata_variables = dataset.get('metadata', [])

            # Add metadata group to list
            if metadata_variables:
                groups.append('MetaData')

            # Filenames to be read into this collection
            filenames = get(dataset, logger, 'filenames')

            # Loop over groups
            for group in groups:

                # Set the variables
                variables_need = variables
                if group is 'MetaData':
                    variables_need = metadata_variables

                # Set the collection name
                collection_name = dataset['name'] + '::' + group

                # Loop over filenames
                for filename in filenames:

                    # Read header part of the file to get coordinates
                    ds_header = xr.open_dataset(filename)

                    # Read the group
                    ds = xr.open_dataset(filename, group=group)

                    # Merge with header part
                    ds = ds.merge(ds_header)

                    # Close the header
                    ds_header.close()

                    # Drop data variables not in user requested variables
                    vars_to_remove = list(set(list(ds.keys())) - set(variables_need))
                    ds = ds.drop_vars(vars_to_remove)

                    # Get channels
                    if 'nchans' in list(ds.dims):
                        nchan_in_file = ds.nchans.size

                        # If user provided no channels then use all channels
                        if nchan == 0:
                            nchan_use = nchan_in_file
                        else:
                            nchan_use = nchan

                        # Keep needed channels
                        if nchan_use < nchan_in_file:
                            ds = ds.sel(nchans=channels)

                        # Add the list of channels to the dataset
                        channel_data_array = xr.DataArray(channels, dims=['nchans'])

                    # Assert that the collection contains at least one variable. If not it is likely
                    # some problem has occurred
                    if not ds.keys():
                        self.logger.abort('Collection \'' + dataset['name'] + ', group ' + group +
                                          '\' in file ' + filename +
                                          ' does not have any variables.')

                    # Add the dataset to the collections
                    data_collections.create_or_add_to_collection(collection_name, ds, 'nlocs')

                    # Close dataset
                    ds.close()

        # Print the contents of the collections for helping the user with making plots
        print(data_collections)
