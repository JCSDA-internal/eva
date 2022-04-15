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

    def create_or_add_to_collection(self, collection_name, collection, concat_dimension=None):

        # Collections should only be xarray datasets
        if not isinstance(collection, xr.Dataset):
            self.logger.abort('In add_collection: collection must be an xarray.Dataset')

        # Check that there is not an existing collection that is empty
        if collection_name in self._collections:
            if not list(self._collections[collection_name].keys()):
                self.logger.abort('In create_or_add_to_collection the collection \'' +
                                  collection_name + '\' is already in existence but appears to ' +
                                  'be empty.')

        # Create the collection or concatenate with existing collection
        # If the collection does not already exist within the dictionary then the incoming
        # collection is used to initialize that collection. If the collection already exists the
        # below will abort, unless a concatenation dimension is offered and it is a valid dimension
        # in the existing collection.
        if collection_name not in self._collections:
            self._collections[collection_name] = collection.copy(deep=False)
        else:
            if concat_dimension is None:
                self.logger.abort('In create_or_add_to_collection the collection \'' +
                                  collection_name + '\' being added already exists. Either ' +
                                  'remove collection or provide a dimension along which to ' +
                                  'concatenate.')
            dims = list(self._collections[collection_name].dims)
            if concat_dimension not in dims:
                self.logger.abort('In create_or_add_to_collection the collection \'' +
                                  collection_name + '\' does not have the dimension \'' +
                                  concat_dimension + '\' that is requested as the dimension ' +
                                  'along which to concatenate. Valid dimensions are ' +
                                  f'{dims}')
            self._collections[collection_name] = xr.concat([self._collections[collection_name],
                                                           collection], dim=concat_dimension)

    # ----------------------------------------------------------------------------------------------

    def add_variable_to_collection(self, collection_name, variable_name, variable):

        # TODO Dataset needs to be created

        # Collections should only be xarray datasets
        if not isinstance(variable, xr.DataArray):
            self.logger.abort('In add_variable_to_collection: variable must be xarray.DataArray')

        self._collections[collection_name][variable_name] = variable

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

    # ----------------------------------------------------------------------------------------------

    def __str__(self):

        # Print a list of variables that are available in the collection
        self.logger.info("Collections available: ", )
        for collection_key in self._collections.keys():
            self.logger.info('')
            self.logger.info('Collection name: ' + collection_key)
            self.logger.info(f'{self._collections[collection_key]}')
        return(' ')

    # ----------------------------------------------------------------------------------------------
