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
from eva.eva_base import EvaBase
from eva.utilities.config import get

# --------------------------------------------------------------------------------------------------


class SocaField(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, dataset_config, data_collections, timing):

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

# --------------------------------------------------------------------------------------------------


def read_soca(file, variable, logger):
    """
    Get true coordinates from the soca_gridspec file
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
