# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------
import re
import scipy
import xarray as xr
from numpy import log, sqrt, mean, abs
from eva.utilities.config import get
from eva.utilities.logger import Logger
from eva.transforms.transform_utils import parse_for_dict, split_collectiongroupvariable
from eva.transforms.transform_utils import replace_cgv
from eva.utilities.utils import remove_list_duplicates
from eva.utilities.utils import remove_empty_from_list_of_strings

defined_functions = ['log', 'sqrt', 'mean', 'scipy_f_ppf', 'scipy_t_ppf', 'abs']

# --------------------------------------------------------------------------------------------------


def scipy_f_ppf(q, df1, df2):
    """
    Wraps xarray around scipy to give scipy.stat.f.ppf
    to get critical value for f test
    q - confidence interval (1-alpha/2) where alpha is the significance level, with confidence
       level being complement (e.g., 1-0.05/2 for a 95% confidence interval)
    df1 - degree of freedom for 1st distribution (count-1)
    df2 - degree of freedome for 2nd distribution (count-1)
    """
    return xr.apply_ufunc(scipy.stats.f.ppf, q, df1, df2)


# --------------------------------------------------------------------------------------------------


def scipy_t_ppf(q, df):
    """
    Wraps xarray around scipy to give scipy.stat.t.ppf
    to get critical value for t test
    q - confidence interval (1-alpha/2 for 2 sided/way, 1-alpha for one sided/way where alpha is
        significance level (e.g., for 95% confidence interval 1-0.05/2 for two sided/way, or
        1-0.05 for one sided/way
    df - degree of freedom (count - 1)
    """
    return xr.apply_ufunc(scipy.stats.t.ppf, q, df)


# --------------------------------------------------------------------------------------------------


def isfloat(a_string):
    """
    Checks if a string can be converted to a floating-point number.

    Args:
        a_string (str): The string to be checked.

    Returns:
        bool: True if the string can be converted to a float, False otherwise.

    This function determines whether a given string can be successfully converted to a
    floating-point number.

    Example:
        ::

                result = isfloat("3.14")
    """

    try:
        float(a_string)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------------------------------


def arithmetic(config, data_collections):
    """
    Applies arithmetic transformations to data variables using specified expressions.

    Args:
        config (dict): A configuration dictionary containing transformation parameters.
        data_collections (DataCollections): An instance of the DataCollections class containing
        input data.

    Returns:
        None

    This function applies arithmetic transformations to data variables within the provided data
    collections. It iterates over the specified collections, groups, and variables, and applies
    arithmetic expressions as defined in the 'equals' expressions within the configuration. The
    resulting variables are added to the data collections.

    Example:
        ::

                config = {
                    'collections': [...],
                    'groups': [...],
                    'variables': [...],
                    'new name': 'result_variable',
                    'equals': '(${collection}::${group}::${var1} + ${collection}::${group}::${var2})
                               / 2'
                }
                arithmetic(config, data_collections)
    """

    # Create a logger
    logger = Logger('ArithmeticTransform')

    # Parse the for dictionary
    [collections, groups, variables] = parse_for_dict(config, logger)

    # Parse config for the expression and new collection/group/variable naming
    new_name_template = get(config, logger, 'new name')
    expression_template = get(config, logger, 'equals')

    # Loop over the templates
    for collection in collections:
        for group in groups:
            for variable in variables:

                # Replace collection, group, variable in template
                [new_name, expression] = replace_cgv(logger, collection, group, variable,
                                                     new_name_template, expression_template)

                # Remove white space
                expression = ''.join(expression.split())

                # Split math equation
                regex_string = r'\(|\)|-|\*|\+|\/|,'
                # add defined functions the user may apply
                for fname in defined_functions:
                    regex_string += r'|\b{}\b'.format(re.escape(fname))
                expression_elements = re.split(regex_string, expression)

                # Remove empty elements and duplicates from expression elements
                expression_elements = remove_empty_from_list_of_strings(expression_elements)
                expression_variables = remove_list_duplicates(expression_elements)

                # Build the expression
                vars = []
                var_counter = 0
                for n in range(len(expression_variables)):
                    if not isfloat(expression_variables[n]):
                        # Extract the data from the collections
                        cgv = split_collectiongroupvariable(logger, expression_variables[n])
                        exp_var_data = data_collections.get_variable_data_array(cgv[0], cgv[1],
                                                                                cgv[2])
                        if exp_var_data is None:
                            logger.info(f'Warning: collection \'{cgv[0]}\' not found, ' +
                                        f'skipping expression \'{expression}\'.')
                            vars = None
                            break
                        vars.append(exp_var_data)
                        # Replace the name in the expression
                        expression = expression.replace(expression_variables[n],
                                                        'vars['+str(var_counter)+']')
                        var_counter = var_counter + 1

                # Skip if any variable was missing (collection not found)
                if vars is None:
                    continue

                # Evaluate the expression
                new_variable = eval(str(expression))
                # Add the new field to the data collections
                cgv = split_collectiongroupvariable(logger, new_name)
                data_collections.add_variable_to_collection(cgv[0], cgv[1], cgv[2], new_variable)


# --------------------------------------------------------------------------------------------------

def generate_arithmetic_config(new_name, expression, collection, var_list):
    """
    Generates a configuration dictionary for the 'arithmetic' transformation.

    Args:
        new_name (str): The new variable name after the transformation.
        expression (str): The arithmetic expression to be applied.
        collection (str): The collection name.
        var_list (list): A list of variables to apply the transformation to.

    Returns:
        dict: A configuration dictionary for the 'arithmetic' transformation.

    This function generates a configuration dictionary for the 'arithmetic' transformation based
    on the provided parameters. It updates the 'new name' field, adjusts the arithmetic expression
    based on the provided collection and group names, and specifies the 'for' dictionary to apply
    the transformation to the specified variables.

    Example:
        ::

                new_name = 'result_variable'
                expression = '(${group1} + ${group2}) / 2'
                collection = 'my_collection'
                var_list = ['variable1', 'variable2']
                config = generate_arithmetic_config(new_name, expression, collection, var_list)
    """

    # Update new_name
    updated_name = collection + '::' + new_name + '::${variable}'

    # Fix expression
    groups = re.split(r'\(|\)|-|\*|\+|\/', expression)
    for group in groups:
        expression = expression.replace(group, collection +
                                        '::' + group + '::${variable}')

    # Build dictionary
    arithmetic_config = {
                        'new name': updated_name,
                        'transform': "arithmetic",
                        'for': {
                          'variable': var_list
                         },
                        'equals': expression
                        }
    return arithmetic_config

# --------------------------------------------------------------------------------------------------
