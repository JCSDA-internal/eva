# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import xarray as xr

from eva.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


class DataCollections:

    def __init__(self):

        # Dictionary to map between collection name and collection itself
        self._collections = {}

        # Create a logger
        self.logger = Logger('DataCollections')

    # ----------------------------------------------------------------------------------------------

    def add_collection(self, collection_name, collection):

        # Collections should only be xarray datasets
        if not isinstance(collection, xr.Dataset):
            self.logger.abort('In add_collection: the collection must be an xarray Dataset')

        self._collections[collection_name] = collection

    # ----------------------------------------------------------------------------------------------

    def get_variable_data(self, variable_name, collection_name=None):

        if collection_name is None and '::' not in variable_name:
            self.logger.abort('In get_variable_data: if collection_name is not provided the '
                              'variable name must contain the collection in the form: '
                              'collection::variable')

        if collection_name is None:
            [collection, variable] = variable_name.split('::')
        else:
            variable = variable_name
            collection = collection_name

        return self._collections[collection][variable].data

    # ------------------------------------------------------------------------------------------
