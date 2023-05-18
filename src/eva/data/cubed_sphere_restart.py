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


def read_nc(files, variable, resolution, logger):
    """
    Given list of ncfiles, variable and resolution, make a 3D variable.
    """
    # Check there are no duplicates in files
    if len(files) != len(set(files)):
        logger.abort('Duplicate files were found in input file ' +
                     f'list: {files}. \nExiting ...')

    # Create empty variable to store data in
    outvar = np.empty((resolution, resolution, len(files)))

    # Loop through nc files and store variable data in outvar
    for i, file in enumerate(files):

        with Dataset(file, mode='r') as f:
            try:
                var = f.variables[variable][:]
            except KeyError:
                logger.abort(f"{variable} is not a valid variable. \nExiting ...")

            if variable in ['lon', 'geolon']:
                var[np.where(var > 180)] = var[np.where(var > 180)] - 360

            outvar[..., i] = var

    return outvar


# --------------------------------------------------------------------------------------------------


class CubedSphereRestart(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, dataset_config, data_collections, timing):

        # Filenames to be read into this collection
        # -----------------------------------------
        fv3_filenames = get(dataset_config, self.logger, 'fv3_filenames')
        orog_filenames = get(dataset_config, self.logger, 'orog_filenames')

        # File variable type
        variable = get(dataset_config, self.logger, 'variable')

        # File resolution
        resolution = get(dataset_config, self.logger, 'resolution')
        resolution = int(resolution.replace('C', ''))

        # Get missing value threshold
        # ---------------------------
        threshold = float(get(dataset_config, self.logger, 'missing_value_threshold', 1.0e30))

        # Get the groups to be read
        # -------------------------
        groups = get(dataset_config, self.logger, 'groups')

        for group in groups:

            # Group name and variables
            group_name = get(group, self.logger, 'name')
            group_vars = get(group, self.logger, 'variables', 'all')

            # Set the collection name
            collection_name = dataset_config['name']

            var_dict = {}

            # Loop through group vars to create data dictionary
            for var in group_vars:
                if var in ['geolon', 'geolat']:
                    var_dict[group_name + '::' + var] = (["lon", "lat", "tile"],
                                                            read_nc(orog_filenames, var,
                                                                    resolution, self.logger))

                else:
                    var_dict[group_name + '::' + var] = (["lon", "lat", "tile"],
                                                            read_nc(fv3_filenames, var,
                                                                    resolution, self.logger))

            # Create dataset_config from data dictionary
            ds = xr.Dataset(var_dict)

            # Assert that the collection contains at least one variable
            if not ds.keys():
                self.logger.abort('Collection \'' + dataset_config['name'] + '\', group \'' +
                                    group_name + '\' in file ' + filename +
                                    ' does not have any variables.')

        # Add the dataset_config to the collections
        data_collections.create_or_add_to_collection(collection_name, ds)

        # Nan out unphysical values
        data_collections.nan_float_values_outside_threshold(threshold)

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()
