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
from eva.eva_base import EvaBase

import importlib
import os


# --------------------------------------------------------------------------------------------------


class DataDriver(EvaBase):

    def execute(self, data_collections, timing):

        # Get list of dataset dictionaries
        datasets = get(self.config, self.logger, 'datasets')

        # Loop over datasets
        for dataset in datasets:

            # Extract name for this diagnostic data type
            try:
                eva_data_class_name = dataset['type']
            except Exception as e:
                msg = '\'type\' key not found. \'diagnostic_data_config\': ' \
                    f'{diagnostic_data_config}, error: {e}'
                raise KeyError(msg)

            # Replace spaces with underscore
            dataset_type = dataset_type.replace(' ', '_')

            # Instantiate the tranform object
            dataset_method = getattr(importlib.import_module('eva.data.'+dataset_type),
                                       dataset_type)

            # Call the dataset
            timing.start(f'dataset: {dataset_type}')
            dataset_method(dataset, data_collections)
            timing.stop(f'dataset: {dataset_type}')

# --------------------------------------------------------------------------------------------------
