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
from netCDF4 import Dataset
from eva.eva_base import EvaBase
from eva.utilities.config import get


# --------------------------------------------------------------------------------------------------


def read_fms_tiles(files, variable, logger):
    """
    Given list of FMS netCDF files and a variable name,
    stitch the files together into N+1 dimension variable
    """
    # Check there are no duplicates in files
    if len(files) != len(set(files)):
        logger.abort('Duplicate files were found in input file ' +
                     f'list: {files}. \nExiting ...')

    # Loop through nc files and store variable data in outvar
    for i, file in enumerate(files):

        with Dataset(file, mode='r') as f:
            try:
                var = f.variables[variable][:]
            except KeyError:
                logger.abort(f"{variable} is not a valid variable. \nExiting ...")

            if variable in ['lon', 'geolon']:
                # transform longitudes to be -180 to 180
                var[np.where(var > 180)] = var[np.where(var > 180)] - 360

            if i == 0:
                # need to create outvar on the first file
                outvar = np.empty(var.shape+len(files), dtype=var.dtype)
            # add values to the correct part of the array
            outvar[..., i] = var

    return outvar


# --------------------------------------------------------------------------------------------------


class CubedSphereRestart(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, dataset_config, data_collections, timing):

        # Filenames to be read into this collection
        # -----------------------------------------
        restart_sets = get(dataset_config, self.logger, 'restart_filenames')
        orog_filenames = get(dataset_config, self.logger, 'orog_filenames')

        # File resolution
        npx = get(dataset_config, self.logger, 'npx')
        npy = get(dataset_config, self.logger, 'npy')
        npz = get(dataset_config, self.logger, 'npz')

        # Get missing value threshold
        # ---------------------------
        threshold = float(get(dataset_config, self.logger, 'missing_value_threshold', 1.0e30))

        # Get collection name
        # ---------------------------
        collection_name = dataset_config['name']

        # Get the variables to be read
        # -------------------------
        orog_vars = get(dataset_config, self.logger, 'orography variables')
        vars_2d = get(dataset_config, self.logger, '2d variables')
        vars_3d = get(dataset_config, self.logger, '3d variables')

        # Read orographic fields first
        # -------------------------
        var_dict = {}
        group_name = 'FV3Orog'
        for var in orog_vars:
            var_dict[group_name + '::' + var] = (["lon", "lat", "tile"],
                                                 read_fms_tiles(orog_filenames, var, self.logger))
        # Create dataset_config from data dictionary
        ds = xr.Dataset(var_dict)

        # Assert that the collection contains at least one variable
        if not ds.keys():
            self.logger.abort('Collection \'' + collection_name + '\', group \'' +
                              group_name + '\' does not have any variables.')

        # Add the dataset_config to the collections
        data_collections.create_or_add_to_collection(collection_name, ds)

        # Loop through sets of RESTART files
        # -------------------------
        for restart_filelist in restart_sets:
            var_dict = {}
            # 2D vars
            group_name = 'FV3Vars2D'
            for var in vars_2d:
                var_dict[group_name + '::' + var] = (["lon", "lat", "tile"],
                                                     read_fms_tiles(restart_filelist,
                                                                    var, self.logger))

            # 3D vars
            group_name = 'FV3Vars3D'
            for var in vars_3d:
                var_dict[group_name + '::' + var] = (["lev", "lon", "lat", "tile"],
                                                     read_fms_tiles(restart_filelist,
                                                                    var, self.logger))

            # Create dataset_config from data dictionary
            ds = xr.Dataset(var_dict)

            # Assert that the collection contains at least one variable
            if not ds.keys():
                self.logger.abort('Collection \'' + collection_name + '\', group \'' +
                                  group_name + '\' does not have any variables.')

            # Add the dataset_config to the collections
            data_collections.create_or_add_to_collection(collection_name, ds)

        # Nan out unphysical values
        data_collections.nan_float_values_outside_threshold(threshold)

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()
