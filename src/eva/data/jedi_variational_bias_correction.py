# (C) Copyright 2024- NOAA/NWS/EMC
#
# (C) Copyright 2024- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import numpy as np
import xarray as xr

from eva.data.eva_dataset_base import EvaDatasetBase
from eva.utilities.config import get


# --------------------------------------------------------------------------------------------------


class JediVariationalBiasCorrection(EvaDatasetBase):

    """
    A class for executing data read for JEDI variational bias correction data.

    Args:
        EvaDatasetBase (class): The base class for dataset processing.

    Attributes:
        N/A

    Methods:
        execute(dataset_config, data_collections, timing):
            Executes data read and transition to data collection for IODA observation space.

        generate_default_config(filenames, collection_name):
            Generates a default configuration dictionary for IODA observation space, used for
            more easily accessing the class interactively.

    Notes:
        - The class inherits from `EvaDatasetBase` and extends its functionality.
    """

    # ----------------------------------------------------------------------------------------------

    def execute(self, dataset_config, data_collections, timing):

        """
        Executes data read for JEDI variational bias correction data.

        Args:
            dataset_config (dict): Configuration settings for the dataset.
            data_collections (DataCollection): The data collection to store read data.
            timing (Timing): Timing information for profiling.

        Returns:
            None
        """

        # Check for required keys in config
        required_keys = [
            'name',
            'bias_file',
            'lapse_file',
            ]
        for key in required_keys:
            self.logger.assert_abort(key in dataset_config, "For JediVariationalBiasCorrection " +
                                     f"the config must contain key: {key}")

        # Parse config
        collection_name = dataset_config['name']
        bias_file = get(dataset_config, self.logger, 'bias_file')
        lapse_file = get(dataset_config, self.logger, 'lapse_file')

        # Read the contents of the bias file (netCDF) into an xarray dataset
        bias_dataset = xr.open_dataset(bias_file)

        # Assign proper coordinates to the dataset and remove nchannels and npredictors from
        # variables
        bias_dataset = bias_dataset.assign_coords(
            {'nchannels': range(len(bias_dataset.nchannels)),
             'npredictors': range(len(bias_dataset.npredictors))
             }
             )

        # Get all the predictor names
        predictor_names = bias_dataset['predictors'].values

        # Initialize a dictionary to store the new data variables
        new_data_vars = {}

        # To eva-rise the dateset we dont want predictor as a dimension, otherwise all the plotting
        # code would have to be made to understand that as a dimension and make that part less
        # generic. Instead we want more variables with predictor as the variable name and the type
        # as the group.
        vars_to_flatter = [
            'bias_coeff_errors',
            'bias_coefficients',
        ]

        # Flatten into new variables with only channel dimension
        for var in vars_to_flatter:
            for i, predictor in enumerate(predictor_names):
                new_data_vars[f'{var}::{predictor}'] = \
                    (['nchannels'], bias_dataset[var].isel(npredictors=i).values)

        # Copy the number_obs_assimilated variable (which only has channel as dimension)
        new_data_vars['bias::number_obs_assimilated'] = \
            (['nchannels'], bias_dataset['number_obs_assimilated'].values)

        # Create a new dataset with the new variables and existing 'channels' and
        # 'number_obs_assimilated'
        flat_dataset = xr.Dataset(
            data_vars=new_data_vars,
            coords={
                'nchannels': bias_dataset['channels'],
            },
            attrs=bias_dataset.attrs
        )

        # Rename the dimension/coordinate from nchannels to channel
        flat_dataset = flat_dataset.rename_dims({'nchannels': 'Channel'})

        # Read the t-lapse file (text) into a dataset
        with open(lapse_file, 'r') as f:
            lapse_data = f.readlines()

        # Store the third element of each line as numpy array
        lapse_data = np.array([float(line.split()[2]) for line in lapse_data])

        # Store lapse data in flat_dataset with channel as dimension/coordinate
        flat_dataset['bias::tlapse'] = xr.DataArray(lapse_data, dims=['Channel'])

        # Add flat_dataset to data_collections
        data_collections.create_or_add_to_collection(collection_name, flat_dataset)

    # ----------------------------------------------------------------------------------------------

    def generate_default_config(self, filenames, collection_name):

        """
        Generates a default configuration dictionary for the class.

        Args:
            filenames (list length 2): List of bias and lapse filenames for the data collection.
            collection_name (str): Name of the data collection.

        Returns:
            dict: A dictionary containing default configuration settings.

        Example:
            ::
                    ioda_instance = JediVariationalBiasCorrection()
                    default_config = ioda_instance.generate_default_config([bias_file, lapse_file],
                                                                           collection_name)
        """

        return {
            'bias_file': filenames[0],
            'lapse_file': filenames[1],
            'name': collection_name
            }

    # ----------------------------------------------------------------------------------------------
