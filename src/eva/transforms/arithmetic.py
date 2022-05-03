# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import re

from eva.utilities.config import get
from eva.utilities.logger import Logger
from eva.utilities.utils import replace_vars, remove_list_duplicates
from eva.utilities.utils import remove_empty_from_list_of_strings


# --------------------------------------------------------------------------------------------------


def arithmetic(config, data_collections):

    # Create a logger
    logger = Logger('ArithmeticTransform')

    # Parse the optional looping dictionary
    optional_looping = get(config, logger, 'optional looping', {})
    collections = get(optional_looping, logger, 'collections', ['none'])
    groups = get(optional_looping, logger, 'groups', ['none'])
    variables = get(optional_looping, logger, 'variables', ['none'])

    # Parse config for the expression and new collection/group/variable naming
    new_collection_name_template = get(config, logger, 'new collection name')
    new_group_name_template = get(config, logger, 'new group name')
    new_variable_name_template = get(config, logger, 'new variable name')
    expression_template = get(config, logger, 'expression')

    # Loop over the templates
    for collection in collections:
        for group in groups:
            for variable in variables:

                # Create dictionary with templates
                tmplt_dict = {}
                if collection is not 'none':
                    tmplt_dict['collection'] = collection
                if group is not 'none':
                    tmplt_dict['group'] = group
                if variable is not 'none':
                    tmplt_dict['variable'] = variable

                # Fill any specified templates
                # ----------------------------
                if tmplt_dict:
                    new_collection_name = replace_vars(new_collection_name_template, **tmplt_dict)
                    new_group_name = replace_vars(new_group_name_template, **tmplt_dict)
                    new_variable_name = replace_vars(new_variable_name_template, **tmplt_dict)
                    expression = replace_vars(expression_template, **tmplt_dict)

                # Assert that no special characters are in the expression
                parse_chars = r'${}'
                if any(parse_char in expression for parse_char in parse_chars):
                    logger.abort(f'The expression \'{expression}\' contains some special '
                                 f'characters ({parse_chars}) that should have been resolved and '
                                 'may disrupt the evaluation step.')

                # Remove white space
                expression = ''.join(expression.split())

                # Split math equation
                expression_elements = re.split(r'\(|\)|-|\*|\+|\/', expression)

                # Remove empty elements
                expression_elements = remove_empty_from_list_of_strings(expression_elements)

                # Remove duplicates
                expression_variables = remove_list_duplicates(expression_elements)

                # Build the expression
                vars = []
                for n in range(len(expression_variables)):
                    # Extract the data from the collections
                    cgv = expression_variables[n].split('::')
                    expression_variable_data = data_collections.get_variable_data_array(cgv[0],
                                                                                        cgv[1],
                                                                                        cgv[2])
                    vars.append(expression_variable_data)
                    # Replace the name in the expression
                    expression = expression.replace(expression_variables[n], 'vars['+str(n)+']')

                # Evaluate the expression
                new_variable = eval(expression)

                # Add the variable to collection
                data_collections.add_variable_to_collection(new_collection_name, new_group_name,
                                                            new_variable_name, new_variable)


# --------------------------------------------------------------------------------------------------
