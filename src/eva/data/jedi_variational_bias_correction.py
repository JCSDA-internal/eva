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

        groups = [
            'BiasCoefficients',
            'BiasCoefficientErrors',
        ]

        # Create a new dataset to store the bias data
        bias_dataset = xr.open_dataset(bias_file)

        # Get record dimension size
        self.logger.assert_abort(len(bias_dataset['Record']) == 1, 'This code currently only  '
                                 'supports reading VarBC files where the Record diminsion is 1')

        # Loop over groups, open and store in bias_dataset
        for group in groups:
            dsg = xr.open_dataset(bias_file, group=group)

            # Rename variables with group
            dsg = dsg.rename_vars({var: f'{group}::{var}' for var in dsg.data_vars})

            # Store the data in the bias_dataset
            bias_dataset = xr.merge([bias_dataset, dsg])

        # Now add coordinate for channels dimension going from 0 to channel
        bias_dataset = bias_dataset.assign_coords(
            {'Channel': range(len(bias_dataset.Channel))}
        )

        # Squeeze the record dimension and remove record coordinate
        bias_dataset = bias_dataset.squeeze('Record')
        bias_dataset = bias_dataset.drop_vars('Record')

        # Rename numberObservationsUsed to Bias::numberObservationsUsed
        bias_dataset = bias_dataset.rename_vars(
            {'numberObservationsUsed': 'Bias::numberObservationsUsed'}
        )

        # Remove attrributes from the dataset
        bias_dataset.attrs = {}

        # Read the t-lapse file (text) into a dataset
        with open(lapse_file, 'r') as f:
            lapse_data = f.readlines()

        # Store the third element of each line as numpy array
        lapse_data = np.array([float(line.split()[2]) for line in lapse_data])

        # Store lapse data in flat_dataset with channel as dimension/coordinate
        bias_dataset['Bias::tlapse'] = xr.DataArray(lapse_data, dims=['Channel'])

        # Add bias_dataset to data_collections
        data_collections.create_or_add_to_collection(collection_name, bias_dataset)

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
