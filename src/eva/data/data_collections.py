# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import numpy as np
import xarray as xr

from eva.utilities.logger import Logger
from eva.utilities.utils import fontColors as fcol, string_does_not_contain


# --------------------------------------------------------------------------------------------------


# Characters that are not permitted in collection, group and variable names.
# Math chars not allowed in order to allow evaluation of the variables in the transforms
disallowed_chars = '-+*/()'


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

        # Check that nothing violates the naming conventions
        self.validate_names()

    # ----------------------------------------------------------------------------------------------

    def add_variable_to_collection(self, collection_name, group_name, variable_name, variable):

        # Assert that new variable is an xarray Dataarray
        if not isinstance(variable, xr.DataArray):
            self.logger.abort('In add_variable_to_collection: variable must be xarray.DataArray')

        # Check that there is not an existing collection that is empty
        if collection_name not in self._collections:
            # Create a new collection to hold the variable
            self._collections[collection_name] = xr.Dataset()

        # Combine the group and variable name
        group_variable_name = group_name + '::' + variable_name

        # Add the variable to the collection
        self._collections[collection_name][group_variable_name] = variable

        # Check that nothing violates the naming conventions
        self.validate_names()

    # ----------------------------------------------------------------------------------------------

    def get_variable_data_array(self, collection_name, group_name, variable_name, channels=None):

        group_variable_name = group_name + '::' + variable_name

        data_array = self._collections[collection_name][group_variable_name]

        if channels is None:
            return data_array
        elif isinstance(channels, int) or not any(not isinstance(c, int) for c in channels):
            # nchans must be a dimension if it will be used for selection
            if 'nchans' not in list(self._collections[collection_name].dims):
                self.logger.abort('In get_variable_data_array channels is provided but nchans ' +
                                  'is not a dimension of the Dataset')
            # Make sure it is a list
            channels_sel = []
            channels_sel.append(channels)
            # Create a new DataArray with the requested channels
            return data_array.sel(nchans=channels_sel)
        else:
            self.logger.abort('In get_variable_data_array channels is neither none or list of ' +
                              'integers')

    # ----------------------------------------------------------------------------------------------

    def get_variable_data(self, collection_name, group_name, variable_name, channels=None):

        variable_array = self.get_variable_data_array(collection_name, group_name, variable_name,
                                                      channels)

        variable_data = variable_array.data

        # Squeeze in case of dimension of 1 (e.g. when 1 channel is needed)
        variable_data = np.squeeze(variable_data)

        return variable_data

    # ----------------------------------------------------------------------------------------------

    def validate_names(self):

        # This code checks that the naming conventions are compliant with what is expected

        for collection_key in self._collections.keys():

            # Assert that the collection name does not contain disallowed characters
            if not string_does_not_contain(disallowed_chars, collection_key):
                self.logger.abort(f'Collection contains the key \'{collection_key}\', which ' +
                                  f'contains a character that is not permitted ' +
                                  f'({disallowed_chars})')

            # Loop over the data variables
            for data_var in list(self._collections[collection_key].data_vars):

                # Assert that the datavar contains '::' identifier, splitting group and variable
                if '::' not in data_var:
                    self.logger.abort(f'Collection \'{collection_key}\' contains the following ' +
                                      f'data variable \'{data_var}\', which does not contain ' +
                                      f'\'::\' splitting the group and variable.')
                [group, variable] = data_var.split('::')
                # Assert that the group name does not contain disallowed characters
                if not string_does_not_contain(disallowed_chars, group):
                    self.logger.abort(f'Collection \'{collection_key}\' contains the following ' +
                                      f'element \'{data_var}\'. The group \'{group}\'' +
                                      f'contains a character that is not permitted ' +
                                      f'({disallowed_chars}).')
                # Assert that the variable name does not contain disallowed characters
                if not string_does_not_contain(disallowed_chars, variable):
                    self.logger.abort(f'Collection \'{collection_key}\' contains the following ' +
                                      f'element \'{data_var}\'. The variable \'{variable}\'' +
                                      f'contains a character that is not permitted ' +
                                      f'({disallowed_chars}).')

    # ----------------------------------------------------------------------------------------------

    def display_collections(self):

        # Display a list of variables that are available in the collection
        self.logger.info('-'*80)
        self.logger.info(fcol.bold + 'Collections available: ' + fcol.end)
        for collection_key in self._collections.keys():
            self.logger.info('')
            self.logger.info('Collection name: ' + fcol.underline + collection_key + fcol.end)
            self.logger.info(f'{self._collections[collection_key]}')
        self.logger.info('-'*80)

    # ----------------------------------------------------------------------------------------------
