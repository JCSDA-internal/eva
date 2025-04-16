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
# from netCDF4 import Dataset
from eva.data.eva_dataset_base import EvaDatasetBase
from eva.utilities.config import get


# --------------------------------------------------------------------------------------------------


def read_fms_tiles(files, variables, logger, use_dask=False):
    """
    Reads specified variables from a list of cubed-sphere NetCDF files,
    stacking across a 'tile' dimension.

    Args:
        files (list): List of NetCDF file paths.
        variables (list): Variables to retain.
        logger: Logger for error handling.
        use_dask (bool): Whether to use Dask for lazy loading.

    Returns:
        dict: {varname: DataArray with 'tile' dimension}
    """
    if len(files) != len(set(files)):
        print(f'Duplicate files were found: {files}. \nExiting ...')

    data_arrays_by_var = {var: [] for var in variables}

    for i, file in enumerate(files):
        try:
            # First open only the metadata (no data loaded)
            with xr.open_dataset(file, chunks={} if use_dask else None) as temp_ds:
                drop_vars = [var for var in temp_ds.variables if var not in variables]

            # Now re-open with drop_variables
            ds = xr.open_dataset(
                file,
                drop_variables=drop_vars,
                chunks={} if use_dask else None
            )
        except Exception as e:
            print(f"Error reading {file}: {e}")

        for var in variables:
            if var not in ds:
                print(f"{var} not found in {file}. \nExiting ...")

            da = ds[var].squeeze()

            if var in ['lon', 'geolon']:
                da = da.where(da <= 180, da - 360)

            da = da.expand_dims(tile=[i])
            data_arrays_by_var[var].append(da)

    # Concatenate and convert to NumPy arrays
    return {var: xr.concat(das, dim='tile').values for var, das in data_arrays_by_var.items()}


    # --------------------------------------------------------------------------------------------------


class CubedSphereRestart(EvaDatasetBase):

    """
    A class for handling Cubed Sphere Restart data.
    """
    
    def execute(self, dataset_config, data_collections, timing):
        """
        Executes the processing of Cubed Sphere Restart data.

        Args:
            dataset_config (dict): Configuration dictionary for the dataset.
            data_collections (DataCollections): Object for managing data collections.
            timing: Timing object for tracking execution time.
        """
        # Filenames to be read into this collection
        # -----------------------------------------
        restart_filenames = get(dataset_config, self.logger, 'restart_filenames')
        orog_filenames = get(dataset_config, self.logger, 'orog_filenames')

        # Get missing value threshold
        # ---------------------------
        threshold = float(get(dataset_config, self.logger, 'missing_value_threshold', 1.0e30))

        # Get collection name
        # -------------------
        collection_name = dataset_config['name']

        # Get the variables to be read
        # ----------------------------
        orog_vars = get(dataset_config, self.logger, 'orography variables')
        vars_2d = get(dataset_config, self.logger, '2d variables', default=[])
        vars_3d = get(dataset_config, self.logger, '3d variables', default=[])

        var_dict = {}

        # Read orographic fields first
        # ----------------------------
        group_name = 'FV3Orog'
        var_arrays = read_fms_tiles(orog_filenames, orog_vars, self.logger, use_dask=False)

        for var in orog_vars:
            var_dict[group_name + '::' + var] = (["lon", "lat", "tile"], var_arrays[var])

        # 2D variables
        # ------------
        group_name = 'FV3Vars2D'
        var_arrays = read_fms_tiles(restart_filenames, vars_2d, self.logger, use_dask=False)

        for var in vars_2d:
            var_dict[group_name + '::' + var] = (["lon", "lat", "tile"], var_arrays[var])

        # 3D variables
        # ------------
        group_name = 'FV3Vars3D'
        var_arrays = read_fms_tiles(restart_filenames, vars_3d, self.logger, use_dask=False)

        for var in vars_3d:
            var_dict[group_name + '::' + var] = (["lev", "lon", "lat", "tile"], var_arrays[var])

        # Create dataset_config from data dictionary
        # ------------------------------------------
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

    # ----------------------------------------------------------------------------------------------

    def generate_default_config(self, filenames, collection_name):

        """
        Generates a default configuration for Cubed Sphere Restart data.

        Args:
            filenames (list): List of file names.
            collection_name (str): Name of the data collection.

        Returns:
            dict: Default configuration dictionary.
        """

        # Needs to be implemented

        pass
