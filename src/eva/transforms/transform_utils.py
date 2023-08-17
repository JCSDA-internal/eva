# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


from eva.utilities.config import get
from eva.utilities.utils import replace_vars_str


# --------------------------------------------------------------------------------------------------


def parse_for_dict(config, logger):
    """
    Parses the 'for' dictionary from the configuration and extracts collection, group, and variable values.

    Args:
        config (dict): A configuration dictionary containing transformation parameters.
        logger (Logger): An instance of the logger for logging messages.

    Returns:
        list: A list containing collection, group, and variable values extracted from the 'for' dictionary.

    This function parses the 'for' dictionary provided in the configuration and extracts the collection, group,
    and variable values specified. It returns a list containing these extracted components.

    Example:
        for_dict = {
            'collection': 'my_collection',
            'group': 'my_group',
            'variable': 'my_variable'
        }
        cgv = parse_for_dict(config, logger)
    """

    # Get the for dict (might not be provided so default to empty dict)
    for_dict = get(config, logger, 'for', {})

    # List of allowable keys
    allowable_keys = ['collection', 'group', 'variable']

    for key in for_dict.keys():
        if key not in allowable_keys:
            logger.abort(f'For dictionary contains the key \'{key}\', which is not permitted. ' +
                         f'Allowable keys are: \'{allowable_keys}\'.')

    # Parse the for loop dictionary
    cgv = []
    cgv.append(get(for_dict, logger, 'collection', ['none']))
    cgv.append(get(for_dict, logger, 'group', ['none']))
    cgv.append(get(for_dict, logger, 'variable', ['none']))

    # Return list of collection group variable
    return cgv


# --------------------------------------------------------------------------------------------------


def replace_cgv(logger, collection, group, variable, *argv):
    """
    Replaces placeholders in template strings with collection, group, and variable values.

    Args:
        logger (Logger): An instance of the logger for logging messages.
        collection (str): The collection value.
        group (str): The group value.
        variable (str): The variable value.
        *argv (str): Variable number of template strings to replace.

    Returns:
        list: A list of template strings with placeholders replaced by corresponding values.

    This function replaces placeholders in the provided template strings with the specified collection,
    group, and variable values. It returns a list of template strings with replaced placeholders.

    Example:
        replaced_templates = replace_cgv(logger, 'my_collection', 'my_group', 'my_variable', template1, template2)
    """

    # Create dictionary with templates
    tmplt_dict = {}
    if collection != 'none':
        tmplt_dict['collection'] = collection
    if group != 'none':
        tmplt_dict['group'] = group
    if variable != 'none':
        tmplt_dict['variable'] = variable

    # Perform replace for the argument list
    arg_replaced = []
    for arg in argv:
        if tmplt_dict:
            arg_replaced.append(replace_vars_str(arg, **tmplt_dict))
        else:
            arg_replaced.append(arg)

    # Assert that the lengths make sense
    if len(arg_replaced) != len(argv):
        logger.abort("In replace_for_dict the length of the output and input is not equal.")

    # Assert that no special characters are left
    for replaced in arg_replaced:
        parse_chars = r'${}'
        if any(parse_char in replaced for parse_char in parse_chars):
            logger.abort(f'The expression \'{replaced}\' contains some special '
                         f'characters ({parse_chars}) that should have been resolved.')

    # Return the arguments with replaced values
    return arg_replaced


# --------------------------------------------------------------------------------------------------


def split_collectiongroupvariable(logger, collectiongroupvariable):
    """
    Splits a collectiongroupvariable string into its components.

    Args:
        logger (Logger): An instance of the logger for logging messages.
        collectiongroupvariable (str): The collectiongroupvariable string to split.

    Returns:
        list: A list containing the collection, group, and variable components.

    This function splits a collectiongroupvariable string into its components (collection, group, variable).
    It returns a list containing these components.

    Example:
        cgv = split_collectiongroupvariable(logger, 'my_collection::my_group::my_variable')
    """

    # Split by double colon
    cgv = collectiongroupvariable.split('::')

    # Assert the correct length
    if len(cgv) != 3:
        logger.abort('split_collectiongroupvariable received \'{collectiongroupvariable}\' but ' +
                     'it has an incorrect format. Expecing \'collection::group::variable\'.')

    # Return list containing three components
    return cgv


# --------------------------------------------------------------------------------------------------
