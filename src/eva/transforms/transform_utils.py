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
from eva.utilities.utils import replace_vars_str


# --------------------------------------------------------------------------------------------------


def parse_for_dict(config, logger):

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

    # Split by double colon
    cgv = collectiongroupvariable.split('::')

    # Assert the correct length
    if len(cgv) != 3:
        logger.abort('split_collectiongroupvariable received \'{collectiongroupvariable}\' but ' +
                     'it has an incorrect format. Expecing \'collection::group::variable\'.')

    # Return list containing three components
    return cgv


# --------------------------------------------------------------------------------------------------
