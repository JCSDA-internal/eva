# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
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


class TransformDriver(EvaBase):

    def execute(self, data_collections, timing):

        # Get list of transform dictionaries
        transforms = get(self.config, self.logger, 'transforms')

        # Loop over transforms
        for transform in transforms:

            # Get the transform type
            transform_type = get(transform, self.logger, 'transform')

            # Replace spaces with underscore
            transform_type = transform_type.replace(' ', '_')

            # Instantiate the tranform object
            transform_method = getattr(importlib.import_module('eva.transforms.'+transform_type),
                                       transform_type)

            # Call the transform
            timing.start(f'Transform: {transform_type}')
            transform_method(transform, data_collections)
            timing.stop(f'Transform: {transform_type}')

        # Display the contents of the collections after updating with transforms
        if transforms:
            self.logger.info('Tranforms complete. Collections after transforms:')
            data_collections.display_collections()


# --------------------------------------------------------------------------------------------------
