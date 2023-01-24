# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from math import sqrt
import re
from statistics import mean

from eva.utilities.config import get
from eva.utilities.logger import Logger
from eva.transforms.transform_utils import parse_for_dict, split_collectiongroupvariable
from eva.transforms.transform_utils import replace_cgv
from eva.utilities.utils import remove_list_duplicates
from eva.utilities.utils import remove_empty_from_list_of_strings


# --------------------------------------------------------------------------------------------------


def channel_stats(config, data_collections):

    # Create a logger
    logger = Logger('ChannelStatsTransform')

    # Define default stat functions to calculate
    if 'statistic list' in config:
        stat_functions = get(config, logger, 'statistic list')
    else:
        stat_functions = ['Mean', 'Std', 'Count', 'Median', 'Min', 'Max']

    # Parse the for dictionary
    [collections, groups, variables] = parse_for_dict(config, logger)

    # Parse config for the expression and new collection/group/variable naming
    variable_name_template = get(config, logger, 'variable_name')

    # Parse config for the channel dimension name
    stat_dim = get(config, logger, 'statistic_dimension', 'Location')

    # Loop over the templates
    for collection in collections:
        for group in groups:
            for variable in variables:

                # Replace collection, group, variable in template
                [variable_name] = replace_cgv(logger, collection, group, variable,
                                              variable_name_template)

                # Extract the data from the collections
                cgv = split_collectiongroupvariable(logger, variable_name)
                exp_var_data = data_collections.get_variable_data_array(cgv[0], cgv[1], cgv[2])

                for stat_function in stat_functions:
                    function_name = getattr(exp_var_data, stat_function.lower())
                    result = function_name(dim=stat_dim)
                    # Add the new field to the data collections
                    cgv = split_collectiongroupvariable(logger, variable_name)
                    data_collections.add_variable_to_collection(cgv[0], cgv[1]+stat_function,
                                                                cgv[2], result)

# --------------------------------------------------------------------------------------------------
