# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from eva.transforms.transform_utils import parse_for_dict, split_collectiongroupvariable
from eva.transforms.transform_utils import replace_cgv
from eva.utilities.config import get
from eva.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------
#  Select a variable by the Time dimension in form YYYYMMDDHH.  If the input is a single time
#  then values for the specified variable will be selected for that cycle and added to
#  data_collections.
#
#  If two cycle times are included they will be used as the bounds for a time slice, and the
#  average of that span will be added to the data_collections.  Note that when specifying a slice
#  the order must be older (lower) to newer (higher).

def select_time(config, data_collections):

    # Create a logger
    logger = Logger('SelectTimeTransform')

    # Parse config for dictionary
    [collections, groups, variables] = parse_for_dict(config, logger)

    # Parse config for the expression and new collection/group/variable naming
    new_name_template = get(config, logger, 'new name')
    starting_field_template = get(config, logger, 'starting field')

    # Get cycles from yaml file and confirm there are 1 or 2 times
    cyc = get(config, logger, 'cycles')
    if type(cyc) is list:
        cycles = cyc
    else:
        cycles = [cyc]

    if None in cycles:
        logger.abort('cycles: for transformation not specified in yaml file. ' +
                     'This should be cycles: followed by 1 or 2 cycle times ' +
                     'in YYYYMMDDHH format.')
    if len(cycles) > 2:
        logger.info('WARNING:  more than 2 cycles specified in yaml file. ' +
                    'Only the first 2 times will be used.')

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
                select_time = data_collections.get_variable_data_array(cgv[0], cgv[1], cgv[2])

                # Get the collection, group, var for new dataset
                cgv_new = split_collectiongroupvariable(logger, new_name)

                # If 2 times, return the mean of a Time slice, else select single Time
                if len(cycles) >= 2:
                    select_time = select_time.sel(Time=slice(str(cycles[0]), str(cycles[1])))
                    select_time = select_time.mean(dim='Time')
                else:
                    select_time = select_time.sel(Time=str(cycles[0]))

                data_collections.add_variable_to_collection(cgv_new[0], cgv_new[1],
                                                            cgv_new[2], select_time)

    data_collections.display_collections()

# --------------------------------------------------------------------------------------------------
