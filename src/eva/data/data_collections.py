# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import numpy as np
from xarray import Dataset, concat, DataArray

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
        if not isinstance(collection, Dataset):
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
            self._collections[collection_name] = concat([self._collections[collection_name],
                                                        collection], dim=concat_dimension)

        # Check that nothing violates the naming conventions
        self.validate_names()

    # ----------------------------------------------------------------------------------------------

    def adjust_channel_dimension_name(self, channel_dimension_name):

        for collection in self._collections.keys():
            if channel_dimension_name in list(self._collections[collection].dims):
                self._collections[collection] = \
                    self._collections[collection].rename_dims({channel_dimension_name: 'Channel'})
                self._collections[collection] = \
                    self._collections[collection].set_index({'Channel': channel_dimension_name})

    # ----------------------------------------------------------------------------------------------

    def add_variable_to_collection(self, collection_name, group_name, variable_name, variable):

        # Assert that new variable is an xarray Dataarray
        if not isinstance(variable, DataArray):
            self.logger.abort('In add_variable_to_collection: variable must be xarray.DataArray')

        # Check that there is not an existing collection that is empty
        if collection_name not in self._collections:
            # Create a new collection to hold the variable
            self._collections[collection_name] = Dataset()

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
            # Channel must be a dimension if it will be used for selection
            if 'Channel' not in list(self._collections[collection_name].dims):
                self.logger.abort(f'In get_variable_data_array channels is provided but ' +
                                  f'Channel is not a dimension in Dataset')
            # Make sure it is a list
            channels_sel = []
            channels_sel.append(channels)

            # Create a new DataArray with the requested channels
            data_array_channels = data_array.sel(Channel=channels_sel)
            return data_array_channels

        else:
            self.logger.abort('In get_variable_data_array channels is neither none or list of ' +
                              'integers')

    # ----------------------------------------------------------------------------------------------

    def get_variable_data(self, collection_name, group_name, variable_name, channels=None):

        variable_array = self.get_variable_data_array(collection_name, group_name, variable_name,
                                                      channels)

        # Extract the actual data array
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

    def nan_float_values_outside_threshold(self, threshold, cgv_to_screen=None):

        # Set the collection, group and variables
        # ---------------------------------------
        if cgv_to_screen is None:
            collections = self._collections.keys()
        else:
            cgv = cgv_to_screen.split('::')
            collections = [cgv[0]]
            groups_variables = [cgv[1]+'::'+cgv[2]]

        # Loop over the collections
        # ------------------------------
        for collection in collections:

            # Set the variables to screen
            # ---------------------------
            if cgv_to_screen is None:
                groups_variables = list(self._collections[collection].data_vars)

            # Loop over the variables and set to nan outside of threshold
            # -----------------------------------------------------------
            for group_variable in groups_variables:

                # Split name into group and variable
                [group, variable] = group_variable.split('::')

                # Get the data
                data_var_value = self.get_variable_data(collection, group, variable)

                # For float data sceen outside threshold
                if 'float' in str(data_var_value.dtype):
                    data_var_value[np.abs(data_var_value) > threshold] = np.nan

    # ----------------------------------------------------------------------------------------------

    def display_collections(self):

        minmaxrms_format_dict = {
            'float64': '{:+.4e}',
            'float32': '{:+.4e}',
            'int64': '{:+11d}',
            'int32': '{:+11d}',
        }

        # Display a list of variables that are available in the collection
        self.logger.info('-'*80)
        self.logger.info(fcol.bold + 'Collections available: ' + fcol.end)
        for collection in self._collections.keys():
            self.logger.info('')
            self.logger.info('Collection name: ' + fcol.underline + collection + fcol.end)
            self.logger.info('\n Dimensions:')
            for dim in list(self._collections[collection].dims):
                dim_value = self._collections[collection].dims[dim]
                self.logger.info(f'  {dim}: {dim_value}')
            self.logger.info('\n Coordinates:')
            for coord in list(self._collections[collection].coords):
                self.logger.info(f'  {coord}')
            self.logger.info('\n Data (group::variable):')
            data_vars = list(self._collections[collection].data_vars)
            max_name_len = len(max(data_vars, key=len))
            for data_var in data_vars:
                group_var = data_var.split('::')
                data_var_value = self.get_variable_data(collection, group_var[0], group_var[1])
                minmaxrms = ''
                if str(data_var_value.dtype) in minmaxrms_format_dict:
                    minmaxrms_format = minmaxrms_format_dict[str(data_var_value.dtype)]
                    min_string = 'Min=' + minmaxrms_format.format(np.nanmin(data_var_value))
                    max_string = 'Max=' + minmaxrms_format.format(np.nanmax(data_var_value))
                    rms_string = ''
                    if str(data_var_value.dtype) == 'float32' or \
                       str(data_var_value.dtype) == 'float64':
                        rms = np.sqrt(np.nanmean(data_var_value**2))
                        rms_string = ', RMS=' + minmaxrms_format.format(rms)
                    minmaxrms_string = ' | ' + min_string + ', ' + max_string + rms_string
                self.logger.info('  ' + data_var.ljust(max_name_len) + ' (' +
                                 str(data_var_value.dtype).ljust(7) + ')' + minmaxrms_string)
        self.logger.info('-'*80)

    # ----------------------------------------------------------------------------------------------
