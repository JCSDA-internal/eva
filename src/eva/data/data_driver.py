# (C) Copyright 2021-2023 NOAA/NWS/EMC
#
# (C) Copyright 2021-2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from eva.utilities.config import get
from eva.data.eva_dataset_base import EvaDatasetFactory

import importlib
import os


# --------------------------------------------------------------------------------------------------

def data_driver(config, data_collections, timing, logger):

    """
    Driver for executing data processing.

    Args:
        config (dict): Configuration settings for data processing.
        data_collections (DataCollections): Instance of the DataCollections class.
        timing (Timing): Timing instance for performance measurement.
        logger (Logger): Logger instance for logging messages.

    """

    # Get list of dataset dictionaries
    datasets = get(config, logger, 'datasets')

    # Loop over datasets
    for dataset in datasets:

        # Extract name for this diagnostic data type
        try:
            eva_data_class_name = dataset['type']
        except Exception as e:
            msg = '\'type\' key not found. \'diagnostic_data_config\': ' \
                f'{diagnostic_data_config}, error: {e}'
            raise KeyError(msg)

        # Create the data object
        creator = EvaDatasetFactory()
        timing.start('DataObjectConstructor')
        eva_data_object = creator.create_eva_object(eva_data_class_name,
                                                    'data',
                                                    logger,
                                                    timing)
        timing.stop('DataObjectConstructor')

        # Prepare diagnostic data
        logger.info(f'Running execute for {eva_data_object.name}')
        timing.start('DataObjectExecute')
        eva_data_object.execute(dataset, data_collections, timing)
        timing.stop('DataObjectExecute')

# --------------------------------------------------------------------------------------------------
