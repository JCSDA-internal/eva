# (C) Copyright 2025- NOAA/NWS/EMC
#
# (C) Copyright 2025- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from eva.transforms.transform_utils import parse_for_dict, split_collectiongroupvariable
from eva.transforms.transform_utils import replace_cgv
from eva.utilities.config import get
from eva.utilities.logger import Logger

def select_dimension(config, data_collections):
    """
    Selects and processes data variables for a specified dimension (e.g., latitude, longitude, depth).

    Args:
        config (dict): A configuration dictionary containing transformation parameters.
        data_collections (DataCollections): An instance of the DataCollections class containing
        input data.

    Returns:
        None

    This function selects and processes data variables within the provided data collections based
    on a specified dimension (e.g., latitude, longitude, depth) and either a single value or a range
    of values for that dimension. The resulting processed variables are added to the data collections.

    Example:
        ::

                config = {
                    'collections': [...],
                    'groups': [...],
                    'variables': [...],
                    'new name': 'dimension_selected_variable',
                    'starting field': 'original_variable',
                    'dimension': 'lat',  # Dimension to select (e.g., lat, lon, depth)
                    'value': 5,  # Single value
                    # OR
                    'start value': -5,
                    'end value': 5  # Range of values
                }
                select_dimension(config, data_collections)
    """

    # Create a logger
    logger = Logger('SelectDimensionTransform')

    # Parse config for dictionary
    [collections, groups, variables] = parse_for_dict(config, logger)

    # Parse config for the expression and new collection/group/variable naming
    new_name_template = get(config, logger, 'new name')
    starting_field_template = get(config, logger, 'starting field')

    # Get the dimension to select
    dimension = get(config, logger, 'dimension', abort_on_failure=True)

    # Get value or start value and end value from yaml file
    values = [None]
    value = get(config, logger, 'value', abort_on_failure=False)
    if value is not None:
        values = [value]
    else:
        start_value = get(config, logger, 'start value', abort_on_failure=False)
        end_value = get(config, logger, 'end value', abort_on_failure=False)
        if start_value is not None and end_value is not None:
            values = [start_value, end_value]

    if None in values:
        logger.abort(f'{dimension} value(s) for transformation not specified in yaml file. '
                     f'This should be either value: value or '
                     f'start value: value and end value: value')
    if len(values) > 2:
        logger.info(f'WARNING: More than 2 {dimension} values specified in yaml file. '
                    f'Only the first 2 values will be used.')

    # Loop over the templates
    for collection in collections:
        for group in groups:
            for variable in variables:

                if variable is not None:
                    # Replace collection, group, variable in template
                    [new_name, starting_field] = replace_cgv(logger, collection, group, variable,
                                                             new_name_template,
                                                             starting_field_template)
                else:
                    new_name = new_name_template
                    starting_field = starting_field_template

                # Get a dataset for the requested collection::group::variable
                cgv = split_collectiongroupvariable(logger, starting_field)
                select_dim = data_collections.get_variable_data_array(cgv[0], cgv[1], cgv[2])

                # Get the collection, group, var for new dataset
                cgv_new = split_collectiongroupvariable(logger, new_name)

                # If a range of values is provided, select the slice; otherwise, select a single value
                if len(values) == 2:
                    if dimension in ['lat', 'lon'] and select_dim[dimension].ndim == 2:
                        # Create a mask for the range
                        mask = (select_dim[dimension] >= values[0]) & (select_dim[dimension] <= values[1])
                        select_dim = select_dim.where(mask, drop=True)
                    else:
                        select_dim = select_dim.sel({dimension: slice(values[0], values[1])})
                else:
                    if dimension in ['lat', 'lon'] and select_dim[dimension].ndim == 2:
                        # Create a mask for the single value
                        mask = select_dim[dimension] == values[0]
                        select_dim = select_dim.where(mask, drop=True)
                    else:
                        select_dim = select_dim.sel({dimension: values[0]}, drop=True)

                data_collections.add_variable_to_collection(cgv_new[0], cgv_new[1],
                                                            cgv_new[2], select_dim)