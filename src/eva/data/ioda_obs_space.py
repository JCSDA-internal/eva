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

            # Assert the correct use of variables and channels
            if ('variables' in dataset and 'channels' in dataset):
                self.logger.abort('Dataset configuraiton for \'' + dataset['name'] + '\'' +
                                  'contains both channels or variables, should be one or ' +
                                  'the other. If channels present, variable is ' +
                                  'brightness_temperature')

            # Get channels or variables
            if ('variables' in dataset):
                variables = dataset['variables']
            elif ('channels' in dataset):
                channels = dataset['channels']
                variables = ['brightness_temperature']  # If channels present variable is bt
            else:
                self.logger.abort('Dataset configuraiton for \'' + dataset['name'] + '\'' +
                                  'contains neither channels or variables.')

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

                    # Open file and add collection
                    with xr.open_dataset(filename, group=group) as ds:

                        # Drop data variables not in user requested variables
                        vars_to_remove = list(set(list(ds.keys())) - set(variables_need))
                        ds = ds.drop_vars(vars_to_remove)

                        # Assert that the collection contains at least one variable. If not it is
                        # likely some problem has occurred
                        if not ds.keys():
                            self.logger.abort('Collection \'' + dataset['name'] + ', group ' +
                                              group + '\' in file ' + filename +
                                              ' does not have any variables.')

                        # Add the dataset to the collections
                        data_collections.create_or_add_to_collection(collection_name, ds, 'nlocs')

            print(data_collections)

            exit()
