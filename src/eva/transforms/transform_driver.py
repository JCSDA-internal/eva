# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from eva.utilities.config import get

import importlib
import os

# --------------------------------------------------------------------------------------------------


def transform_driver(config, data_collections, timing, logger):
    """
    Applies a series of transformation methods to data collections.

    Args:
        config (dict): A configuration dictionary containing transformation parameters.
        data_collections (DataCollections): An instance of the DataCollections class containing input data.
        timing (Timing): An instance of the Timing class for tracking execution times.
        logger (Logger): An instance of the logger for logging messages.

    Returns:
        None

    This function applies a series of transformation methods to the provided data collections. It iterates over
    a list of transform dictionaries specified in the configuration. For each transform, it identifies the
    transform type, instantiates the corresponding transform object, and calls the transform method.
    Execution times for each transform are tracked using the Timing instance.

    """

    # Get list of transform dictionaries
    transforms = get(config, logger, 'transforms')

    # Loop over transforms
    for transform in transforms:

        # Get the transform type
        transform_type = get(transform, logger, 'transform')

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
        logger.info('Tranforms complete. Collections after transforms:')
        data_collections.display_collections()


# --------------------------------------------------------------------------------------------------
