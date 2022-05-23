# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from eva.utilities.config import get
from eva.utilities.logger import Logger
from eva.utilities.utils import replace_vars


# --------------------------------------------------------------------------------------------------


def accept_where(config, data_collections):

    # Create a logger
    logger = Logger('RejectWhereTransform')

    # Parse the optional looping dictionary
    data_to_filter = get(config, logger, 'data to filter')
    collections = get(data_to_filter, logger, 'collections')
    groups = get(data_to_filter, logger, 'groups')
    variables = get(data_to_filter, logger, 'variables')

    # Parse config for the expression and new collection/group/variable naming
    new_names = get(config, logger, 'new names')
    new_collection_name_template = get(new_names, logger, 'collection')
    new_group_name_template = get(new_names, logger, 'group')
    new_variable_name_template = get(new_names, logger, 'variable')

    # Get the where dictionary
    wheres = get(config, logger, 'where')

    # Loop over the templates
    for collection in collections:
        for group in groups:
            for variable in variables:

                # Create dictionary with templates
                tmplt_dict = {}
                tmplt_dict['collection'] = collection
                tmplt_dict['group'] = group
                tmplt_dict['variable'] = variable

                # Fill any templates
                new_collection_name = replace_vars(new_collection_name_template, **tmplt_dict)
                new_group_name = replace_vars(new_group_name_template, **tmplt_dict)
                new_variable_name = replace_vars(new_variable_name_template, **tmplt_dict)

                # Get the variable to be adjusted
                var_to_filter = data_collections.get_variable_data_array(collection, group,
                                                                         variable)

                # Loop over wheres and create new variable with NaN where filtered
                for where_expression in wheres:

                    # Assertions on where expression
                    where_exp_elems = where_expression.split(' ')
                    if len(where_exp_elems) != 3:
                        self.logger.abort(f'Where expression \'{where_expression}\' does not ' +
                                          'have three space seperated elements. Should be of the ' +
                                          'form \'variable condition value\', e.g. ' +
                                          '\'${collection}::${group}::${variable} >= 0.0\'.')
                    if '::' not in where_exp_elems[0]:
                        self.logger.abort('The first element of the where expression ' +
                                          f'\'{where_expression}\' does not contain \'::\'.' +
                                          'Form should be: ${collection}::${group}::${variable}')

                    # Replace templated aspects
                    where_exp_elems[0] = replace_vars(where_exp_elems[0], **tmplt_dict)

                    # Get collection, group and variable name
                    where_exp_cgv = where_exp_elems[0].split('::')

                    # Extract Dataarray for that variable
                    where_var = data_collections.get_variable_data_array(where_exp_cgv[0],
                                                                         where_exp_cgv[1],
                                                                         where_exp_cgv[2])

                    # Perform evaluation to filter the variable
                    where_string = 'where_var ' + where_exp_elems[1] + ' ' + where_exp_elems[2]
                    var_to_filter = eval('var_to_filter.where(' + where_string + ')')

                    # Add the variable to collection
                data_collections.add_variable_to_collection(new_collection_name, new_group_name,
                                                            new_variable_name, var_to_filter)


# --------------------------------------------------------------------------------------------------
