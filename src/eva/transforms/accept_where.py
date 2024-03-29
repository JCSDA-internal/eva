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
    """
    Applies a filtering transformation to data variables based on specified conditions.

    Args:
        config (dict): A configuration dictionary containing transformation parameters.
        data_collections (DataCollections): An instance of the DataCollections class containing
        input data.

    Returns:
        None

    Raises:
        ValueError: If the 'where' expression format is incorrect.

    This function applies a filtering transformation to data variables within the provided
    data collections. It iterates over the specified collections, groups, and variables, and
    applies filtering conditions as defined in the 'where' expressions within the configuration.
    The resulting filtered variables are added to the data collections.

    Example:
        ::

                config = {
                    'collections': [...],
                    'groups': [...],
                    'variables': [...],
                    'new name': 'filtered_variable',
                    'starting field': 'original_variable',
                    'where': ['${collection}::${group}::${variable} >= 0.0']
                }
                accept_where(config, data_collections)
    """

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

def generate_accept_where_config(new_name, starting_field, where, collection, var_list):
    """
    Generates a configuration dictionary for the 'accept where' transformation.

    Args:
        new_name (str): The new variable name after the transformation.
        starting_field (str): The starting variable field for the transformation.
        where (list): A list of filter expressions to be applied.
        collection (str): The collection name.
        var_list (list): A list of variables to apply the transformation to.

    Returns:
        dict: A configuration dictionary for the 'accept where' transformation.

    This function generates a configuration dictionary for the 'accept where' transformation based
    on the provided parameters. It updates the 'new name' and 'starting field' fields, adjusts
    expressions in 'where' based on the provided collection and group names, and specifies the
    'for' dictionary to apply the transformation to the specified variables.

    Example:
        ::
                new_name = 'filtered_variable'
                starting_field = 'original_variable'
                where = ['group1 >= 0', 'group2 < 10']
                collection = 'my_collection'
                var_list = ['variable1', 'variable2']
                config = generate_accept_where_config(new_name, starting_field, where,
                                                      collection, var_list)
    """

    # Update new_name
    updated_name = collection + '::' + new_name + '::${variable}'
    starting_field = collection + '::' + starting_field + '::${variable}'

    for index, expression in enumerate(where):
        # Get group
        group, _, _ = expression.split(' ')
        # Fix group name in expression
        where[index] = expression.replace(group, collection +
                                          '::' + group + '::${variable}')
    # Build config
    accept_where_config = {
                            'new name': updated_name,
                            'where': where,
                            'transform': 'accept where',
                            'starting field': starting_field,
                            'for': {
                                "variable": var_list
                            }
                          }
    return accept_where_config

# --------------------------------------------------------------------------------------------------
