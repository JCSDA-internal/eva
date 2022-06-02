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


def accept_where(config, data_collections):

    # Create a logger
    logger = Logger('AcceptWhereTransform')

    # Parse the for dictionary
    [collections, groups, variables] = parse_for_dict(config, logger)

    # Parse config for the expression and new collection/group/variable naming
    new_name_template = get(config, logger, 'new name')
    starting_field_template = get(config, logger, 'starting field')

    # Get the where dictionary
    wheres = get(config, logger, 'where')

    # Loop over the templates
    for collection in collections:
        for group in groups:
            for variable in variables:

                # Replace collection, group, variable in template
                [new_name, starting_field] = replace_cgv(logger, collection, group, variable,
                                                         new_name_template, starting_field_template)

                # Get the variable to be adjusted
                cgv = split_collectiongroupvariable(logger, starting_field)
                var_to_filter = data_collections.get_variable_data_array(cgv[0], cgv[1], cgv[2])

                # Loop over wheres and create new variable with NaN where filtered
                for where_expression in wheres:

                    # Split where into variable, condition and value
                    try:
                        [where_var, where_con, where_val] = where_expression.split(' ')
                    except Exception:
                        self.logger.abort(f'Failed to split \'{where_expression}\'. Check that ' +
                                          'it has the correct format, e.g. ' +
                                          '\'${collection}::${group}::${variable} >= 0.0\'.')

                    # Replace templated aspects in where statement
                    [where_var] = replace_cgv(logger, collection, group, variable, where_var)

                    # Extract Dataarray for that variable
                    cgv = split_collectiongroupvariable(logger, where_var)
                    where_var_dat = data_collections.get_variable_data_array(cgv[0], cgv[1], cgv[2])

                    # Perform evaluation to filter the variable
                    where_string = 'where_var_dat ' + where_con + ' ' + where_val
                    var_to_filter = eval('var_to_filter.where(' + where_string + ')')

                # Add the variable to collection
                cgv = split_collectiongroupvariable(logger, new_name)
                data_collections.add_variable_to_collection(cgv[0], cgv[1], cgv[2], var_to_filter)


# --------------------------------------------------------------------------------------------------
