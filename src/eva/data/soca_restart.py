# (C) Copyright 2023- NOAA/NWS/EMC
#
# (C) Copyright 2023- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import numpy as np
import xarray as xr
from netCDF4 import Dataset
from eva.utilities.config import get
from eva.data.eva_dataset_base import EvaDatasetBase

# --------------------------------------------------------------------------------------------------


class SocaRestart(EvaDatasetBase):

    """
    A class for reading and processing SOCA restart data.

    This class inherits from `EvaDatasetBase` and provides methods to read and process SOCA restart
    data, including orographic fields and SOCA variables. The processed data is added to the data
    collections.

    Args:
        EvaDatasetBase (class): The base class for EVITA dataset operations.

    Methods:
        execute(dataset_config, data_collections, timing):
            Process SOCA restart data and add it to the data collections.
            Args:
                dataset_config (dict): Configuration for the dataset.
                data_collections (EvaDataCollections): Data collections to which the processed data
                will be added.
                timing: Timing information.

        generate_default_config(filenames, collection_name):
            Generate the default configuration for the dataset.
            Args:
                filenames: Filenames.
                collection_name: Name of the collection.
    """

    def execute(self, dataset_config, data_collections, timing):

        """
        Process SOCA restart data and add it to the data collections.

        Args:
            dataset_config (dict): Configuration for the dataset.
            data_collections (EvaDataCollections): Data collections to which the processed data will
            be added.
            timing: Timing information.
        """

        # Filenames to be read into this collection
        # -----------------------------------------
        soca_filenames = get(dataset_config, self.logger, 'soca_filenames')
        geometry_file = get(dataset_config, self.logger, 'geometry_file')

        # Get missing value threshold
        # ---------------------------
        threshold = float(get(dataset_config, self.logger, 'missing_value_threshold', 1.0e20))

        # Get collection name
        # ---------------------------
        collection_name = dataset_config['name']

        # Get the variables to be read
        # -------------------------
        soca_vars = get(dataset_config, self.logger, 'variables', default=[])
        coord_vars = get(dataset_config, self.logger, 'coordinate variables', default=None)

        # Read orographic fields first
        # -------------------------
        var_dict = {}
        group_name = 'SOCAgrid'
        for var in coord_vars:
            dims, data = read_soca(geometry_file, var, self.logger)
            var_dict[group_name + '::' + var] = (dims, data)

        # SOCA variables
        # -------------------------
        group_name = 'SOCAVars'
        for var in soca_vars:
            dims, data = read_soca(soca_filenames, var, self.logger)
            var_dict[group_name + '::' + var] = (dims, data)

        # Create dataset_config from data dictionary
        # -------------------------
        ds = xr.Dataset(var_dict)

        # Assert that the collection contains at least one variable
        # -------------------------
        if not ds.keys():
            self.logger.abort('Collection \'' + collection_name + '\', group \'' +
                              group_name + '\' does not have any variables.')

        # Add the dataset_config to the collections
        # -------------------------
        data_collections.create_or_add_to_collection(collection_name, ds)

        # Nan out unphysical values
        # -------------------------
        data_collections.nan_float_values_outside_threshold(threshold)

        # Display the contents of the collections for helping the user with making plots
        # -------------------------
        data_collections.display_collections()

    # ----------------------------------------------------------------------------------------------

    def generate_default_config(self, filenames, collection_name):

        """
        Generate a default configuration for the dataset.

        This method generates a default configuration for the dataset based on the provided
        filenames and collection name. It can be used as a starting point for creating a
        configuration for the dataset.

        Args:
            filenames: Filenames or file paths relevant to the dataset.
            collection_name (str): Name of the collection for the dataset.

        Returns:
            dict: A dictionary representing the default configuration for the dataset.
        """

        pass

# --------------------------------------------------------------------------------------------------


def read_soca(file, variable, logger):

    """
    Read SOCA data from the specified file for the given variable.

    Args:
        file (str): Path to the SOCA data file.
        variable (str): Name of the variable to read.
        logger: Logger for logging messages.

    Returns:
        tuple: A tuple containing dimensions (list) and data (numpy.ndarray) for the specified
        variable.
    """

    with Dataset(file, mode='r') as f:
        try:
            dims = ["lon", "lat"]
            if len(f.variables[variable].dimensions) > 3:
                dims = ["lev", "lon", "lat"]
            var = np.squeeze(f.variables[variable][:])
        except KeyError:
            logger.abort(f"{variable} is not a valid variable. \nExiting ...")

    return dims, var

# --------------------------------------------------------------------------------------------------
