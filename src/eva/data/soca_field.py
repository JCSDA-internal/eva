# (C) Copyright 2022-2023 NOAA/NWS/EMC
#
# (C) Copyright 2022-2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import numpy as np
import xarray as xr
import yaml
from netCDF4 import Dataset
from eva.eva_base import EvaBase
from eva.utilities.config import get

SOCA_yaml = '''
MOM6:
    init: ocn
    grid:
        group_name: SOCAgrid
    2Dvariables:
        group_name: SOCAVars2D
        vars:
            - ave_ssh
    3Dvariables:
        group_name: SOCAVars3D
        vars:
            - Temp
            - Salt
            - h
            - u
            - v
# CICE6:
#     variables:
# SFC:
#     variables:
# WAV:
#     variables:
'''



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
        threshold = float(get(dataset_config, self.logger, 'missing_value_threshold', 1.0e30))

        # Get collection name
        # ---------------------------
        collection_name = dataset_config['name']
        data = yaml.safe_load(SOCA_yaml)

        # Get the variables to be read
        # -------------------------
        # vars_2d = get(dataset_config, self.logger, 'variables', default=[])
        vars = get(dataset_config, self.logger, 'variables', default=[])
        coord_vars = get(dataset_config, self.logger, 'coordinate variables', default=None)

        # Read orographic fields first
        # -------------------------
        var_dict = {}
        group_name = data['MOM6']['grid']['group_name']
        for var in coord_vars:
            var_dict[group_name + '::' + var] = (["lon", "lat"], read_2d_grid(geometry_file, var, self.logger))


        # 2D variables
        # -------------------------
        group_name = 'SOCAVars2D'
        for var in vars:
            var_dict[group_name + '::' + var] = (["lon", "lat"],
                                                 read_2d_grid(soca_filenames,
                                                                var, self.logger))

        # 3D variables
        # -------------------------
        # group_name = 'SOCAVars3D'
        # var = 'Salt'
        # var_dict[group_name + '::' + var] = (["lev", "lon", "lat"],
        #                                      read_2d_grid(soca_filenames,
        #                                                   var, self.logger))

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

        # print(var_dict)
        # Nan out unphysical values
        # -------------------------
        # data_collections.nan_float_values_outside_threshold(threshold)

        # Display the contents of the collections for helping the user with making plots
        # -------------------------
        data_collections.display_collections()
        # print(ds)
        # exit()

# --------------------------------------------------------------------------------------------------


def read_2d_grid(file, variable, logger):
    """
    Get true coordinates from the soca_gridspec file
    """
    with Dataset(file, mode='r') as f:
        try:
            print(len(f.variables[variable].dimensions))
            exit()
            var = np.squeeze(f.variables[variable][:])
        except KeyError:
            logger.abort(f"{variable} is not a valid variable. \nExiting ...")

    return var

# --------------------------------------------------------------------------------------------------


def read_3d_grid(file, variable, logger):
    """
    Get true coordinates from the soca_gridspec file
    """
    with Dataset(file, mode='r') as f:
        try:
            var = np.squeeze(f.variables[variable][:])
        except KeyError:
            logger.abort(f"{variable} is not a valid variable. \nExiting ...")

    return var
    # # Loop through nc files and store variable data in outvar
    # for i, file in enumerate(files):

    #     with Dataset(file, mode='r') as f:
    #         try:
    #             var = np.squeeze(f.variables[variable][:])
    #         except KeyError:
    #             logger.abort(f"{variable} is not a valid variable. \nExiting ...")

    #         if variable in ['lon', 'geolon']:
    #             # transform longitudes to be -180 to 180
    #             var[np.where(var > 180)] = var[np.where(var > 180)] - 360

    #         if i == 0:
    #             # need to create outvar on the first file
    #             outvar = np.empty(var.shape+(len(files),), dtype=var.dtype)
    #         # add values to the correct part of the array
    #         outvar[..., i] = var