# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import re
import string
import yaml

from eva.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


class fontColors:
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


# --------------------------------------------------------------------------------------------------


def camelcase_to_underscore(CamelCaseString):

    """
    Convert a CamelCase string to underscore_separated lowercase string.

    Args:
        CamelCaseString (str): The CamelCase string to be converted.

    Returns:
        str: The underscore-separated lowercase string.
    """

    # Create empty output string
    underscore_string = ''

    if not isinstance(CamelCaseString, str):
        msg = f'\'diagnostic name\': {CamelCaseString} - should be a str type. ' \
              f'Was actually a type: {type(CamelCaseString)}'
        raise TypeError(msg)

    # limit string to lower case or uppercase letters
    if not CamelCaseString.isalpha():
        msg = 'Only a-z A-Z characters allowed in module name. ' \
              f'Module name was: {CamelCaseString}, should be \'CamelCaseString\'.'
        raise ValueError(msg)

    # Loop over the elements in the string
    for element in CamelCaseString:

        # Check if element is upper case and if so prepend with underscore
        if element.isupper():
            new_element = '_'+element.lower()
        else:
            new_element = element

        # Add new element to the output string
        underscore_string = underscore_string+new_element

    # If this results in leading underscore then remove it
    if underscore_string[0] == "_":
        underscore_string = underscore_string[1:]

    return underscore_string


# --------------------------------------------------------------------------------------------------


def load_yaml_file(eva_config, logger):

    """
    Load a YAML file into a dictionary.

    Args:
        eva_config (str): Path to the YAML file.
        logger (Logger): The logger object for logging messages.

    Returns:
        dict: A dictionary containing the contents of the YAML file.
    """

    if logger is None:
        logger = Logger('LoadYamlFile')

    try:
        with open(eva_config, 'r') as eva_config_opened:
            eva_dict = yaml.safe_load(eva_config_opened)
    except Exception as e:
        logger.abort('Eva diagnostics is expecting a valid yaml file, but it encountered ' +
                     f'errors when attempting to load: {eva_config}, error: {e}')

    return eva_dict


# --------------------------------------------------------------------------------------------------


def get_schema(YamlFile, configDict={}, logger=None):

    """
    Read a YAML file into a dictionary containing a configuration and overwrite the default
    configuration with the input configDict.

    Args:
        YamlFile (str): Path to the YAML file.
        configDict (dict, optional): Dictionary of configuration options to overwrite defaults.
            Defaults to an empty dictionary.
        logger (Logger, optional): The logger object for logging messages. Defaults to None.

    Returns:
        dict: A dictionary containing the configuration.
    """

    if logger is None:
        logger = Logger('EvaSchema')

    # ignore some fields
    skipvars = ['type', 'comparison']

    # read schema from YAML file
    fullConfig = load_yaml_file(YamlFile, logger)

    # update full config dict based on input configDict
    for key, value in configDict.items():
        if key in fullConfig or skipvars:
            logger.trace(f'{key}:{value}')
            fullConfig[key] = value
        else:
            msg = f"'{key}' not in default schema. Not a valid entry."
            raise ValueError(msg)

    return fullConfig


# --------------------------------------------------------------------------------------------------


def update_object(myObj, configDict, logger=None):

    """
    Update the attributes of the input object myObj based on a dictionary configDict and return a
    new, updated myObj.

    Args:
        myObj (object): The object to be updated.
        configDict (dict): Dictionary containing attribute names and their corresponding values to
        update.
        logger (Logger, optional): The logger object for logging messages. Defaults to None.

    Returns:
        object: The updated object with modified attributes.
    """

    if logger is None:
        logger = Logger('EvaUpdateObject')

    # loop through input dictionary, update input object key values
    for key, value in configDict.items():
        if key in dir(myObj):
            logger.trace(f"Updating '{key}'")
        else:
            logger.trace(f"Adding '{key}'")
        setattr(myObj, key, value)

    return myObj


# --------------------------------------------------------------------------------------------------


def parse_channel_list(channels_str_or_list, logger):

    """
    Parse the input channels_str_or_list and return a list of channel numbers.

    This function handles parsing and converting various input types into a list of channel numbers.

    Args:
        channels_str_or_list (list, str, int): The input channels as a list, string, or integer.
        logger (Logger): The logger object for logging error messages.

    Returns:
        list: A list of channel numbers.

    Raises:
        ValueError: If the input is not a valid list of integers or a string that can be parsed into
                    a list of integers.
    """

    # If the input is an empty list return an empty list
    if channels_str_or_list is []:
        channel_list = []
        return channel_list

    # Check if the input is already a list
    if isinstance(channels_str_or_list, list):

        # Check if
        if all(isinstance(x, int) for x in channels_str_or_list):
            return channels_str_or_list
        else:
            logger.abort('In parse_channel_list the input is a list but not all elements are ' +
                         'integers. Either use a string or pass a list of integers.')

    elif isinstance(channels_str_or_list, str):

        # Convert the string
        channel_list = []
        for x in channels_str_or_list.split(','):
            if '-' in x:
                lnum, rnum = x.split('-')
                lnum, rnum = int(lnum), int(rnum)
                channel_list.extend(range(lnum, rnum + 1))
            else:
                lnum = int(x)
                channel_list.append(lnum)

        return channel_list

    elif isinstance(channels_str_or_list, int):

        # Convert int to list
        channel_list = [channels_str_or_list]
        return channel_list

    else:

        logger.abort('In parse_channel_list the input is neither a list of integers or a string ' +
                     'that can be parsed into a list of integers.')


# --------------------------------------------------------------------------------------------------


def replace_vars_str(s, **defs):

    """
    Interpolate and replace variables in the input string.

    This function replaces variable placeholders in the input string with their corresponding values
    provided in the 'defs' dictionary. It can handle recursive variable substitution.

    Parameters:
        s (str): The input string containing variables to be resolved.
        defs (dict): A dictionary of variable definitions for resolving variables, expressed as
                     key-word arguments.

    Returns:
        str: The interpolated string. Undefined variables are left unchanged.

    Example:
        If defs = {'var1': 'value1', 'var2': 'value2'}, and s = 'This is ${var1} and ${var2}.',
        the returned string would be 'This is value1 and value2.'
    """

    expr = s

    # Resolve special variables: ${var}
    for var in re.findall(r'\$\{(\w+)\}', expr):
        if var in defs:
            expr = re.sub(r'\$\{'+var+r'\}', defs[var], expr)

    # Resolve defs
    s_interp = string.Template(expr).safe_substitute(defs)

    # Recurse until no substitutions remain
    if s_interp != s:
        s_interp = replace_vars_str(s_interp, **defs)

    return s_interp


# --------------------------------------------------------------------------------------------------


def replace_vars_dict(d, **defs):

    """
    Replace variable placeholders in the dictionary values using provided definitions.

    This function replaces variable placeholders in the dictionary values with their corresponding
    values provided in the 'defs' dictionary. It searches for placeholders in the dictionary
    values and substitutes them with their definitions.

    Parameters:
        d (dict): The dictionary to be modified.
        defs (dict): A dictionary of variable definitions for resolving variables, expressed as
                     key-word arguments.

    Returns:
        dict: The modified dictionary with variable placeholders replaced by their definitions.

    Example:
        If defs = {'swell_dir': '/path/to/swell'},
        and d = {'key': '$(swell_dir)/some/file.ext'},
        the returned dictionary would be {'key': '/path/to/swell/some/file.ext'}.
    """

    # Convert dictionary to string representation in yaml form
    d_string = yaml.dump(d)

    # Replace the definitions everywhere in the dictionary
    d_string = replace_vars_str(d_string, **defs)

    # Convert back to dictionary
    d_interp = yaml.safe_load(d_string)

    return d_interp

# --------------------------------------------------------------------------------------------------


def replace_vars_notebook(nb, **defs):

    """
    Replace variable placeholders in a nbconvert NotebookNode's cell source code.

    This function iterates through the cells of a nbconvert NotebookNode, searching for variable
    placeholders in the cell source code. Variable placeholders are then substituted with their
    corresponding definitions provided in the 'defs' dictionary.

    Parameters:
        nb (NotebookNode): A nbconvert dict-like NotebookNode to be modified.
        defs (dict): A dictionary of variable definitions for resolving variables, expressed as
                     key-word arguments.

    Returns:
        NotebookNode: The modified nbconvert NotebookNode with variable placeholders in cell
                      source code replaced by their definitions.

    Example:
        If defs = {'swell_dir': '/path/to/swell'},
        and a cell source code contains 'file_path = $(swell_dir)/file.txt',
        the modified cell source code will be 'file_path = /path/to/swell/file.txt'.
    """

    # Iterate through notebook cells, skipping notebook metadata
    for idx, cell in enumerate(nb['cells'][1:]):
        source = str(cell['source'])
        for key, value in defs.items():
            overwrite_found = source.find(key)
            if (overwrite_found > 0):
                # Only pass subsection from dictionary that's needed
                d = {key: value}
                new_source = replace_vars_str(source, **d)
                # Update notebook cell
                nb['cells'][idx+1]['source'] = new_source
    return nb


# --------------------------------------------------------------------------------------------------


def remove_list_duplicates(input_list):

    """
    Remove duplicate elements from a list while preserving the order.

    Parameters:
        input_list (list): The input list containing elements.

    Returns:
        list: A new list with duplicate elements removed while preserving the order.
    """

    output_list = []
    [output_list.append(x) for x in input_list if x not in output_list]

    return output_list


# --------------------------------------------------------------------------------------------------


def remove_empty_from_list_of_strings(list):

    """
    Remove empty strings from a list of strings.

    Parameters:
        lst (list): The input list of strings.

    Returns:
        list: A new list with empty strings removed.
    """

    while ("" in list):
        list.remove("")

    return list


# --------------------------------------------------------------------------------------------------


def string_does_not_contain(disallowed_chars, string_to_check):

    """
    Check if a string does not contain any of the specified characters.

    Parameters:
        disallowed_chars (str): A string containing characters that should not be present in
                                'string_to_check'.
        string_to_check (str): The string to be checked.

    Returns:
        bool: True if 'string_to_check' does not contain any of the 'disallowed_chars', False
              otherwise.
    """

    string_does_not_contain_flag = True
    if any(disallowed_char in string_to_check for disallowed_char in disallowed_chars):
        string_does_not_contain_flag = False

    return string_does_not_contain_flag


# --------------------------------------------------------------------------------------------------


def slice_var_from_str(config, datavar, logger):

    """
    Slice a variable from an array based on the configuration.

    This function evaluates the slicing configuration and applies it to the input variable
    'datavar'.

    Parameters:
        config (dict): The configuration dictionary containing slicing information.
        datavar: The input variable to be sliced.
        logger (Logger): The logger object for logging messages.

    Returns:
        The sliced variable 'datavar'.
    """

    if 'slices' in config.keys():
        try:
            datavar = eval("datavar"+config['slices'])
        except IndexError:
            logger.send_message('ABORT', f"IndexError: {config['variable']}" +
                                         f" has dimensions {datavar.shape}" +
                                         f" and input slices string is {config['slices']}")
    return datavar


# --------------------------------------------------------------------------------------------------


def is_number(s):

    """
    Check if a given value can be converted to a number.

    Parameters:
        s: The value to be checked.

    Returns:
        bool: True if the value can be converted to a number, False otherwise.
    """

    try:
        float(s)
        return True
    except ValueError:
        return False

# --------------------------------------------------------------------------------------------------
