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

    # Convert a string that looks like e.g. ThisIsAString to this_is_a_string
    # -----------------------------------------------------------------------

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
    # utility function to help load a yaml file into a dict.

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
    # read YamlFile into a dictionary containing a configuration,
    # and overwrite the default configuration with the input configDict

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
    # update input object myObj attributes based on a dictionary
    # and return a new, updated myObj

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
    """Interpolate/replace variables in string

    Resolved variable formats is: ${var}. Undefined
    variables remain unchanged in the returned string. This method will
    recursively resolve variables of variables.

    Parameters
    ----------
    s : string, required
        Input string containing variables to be resolved.
    defs: dict, required
        dictionary of definitions for resolving variables expressed
        as key-word arguments.

    Returns
    -------
    s_interp: string
        Interpolated string. Undefined variables are left unchanged.
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
    At the highest level of the dictionary are definitions, such as swell_dir: /path/to/swell.
    Elsewhere in the dictionary is use of these definitions, such as key: $(swell_dir)/some/file.ext
    In this script variables like $(swell_dir) are replaced everywhere in the dictionary using the
    definition.

    Parameters
    ----------
    d : dictionary, required
        Dictionary to be modified
    defs: dictionary, required
          Dictionary of definitions for resolving variables expressed as key-word arguments.

    Returns
    -------
    d_interp: dictionary
              Dictionary with any definitions resolved
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
    Parameters
    ----------
    nb : NotebookNode, required
        nbconvert dict-like NotebookNode to be modified
    defs: dictionary, required
          Dictionary of definitions for resolving variables expressed as key-word arguments.

    Returns
    -------
    nb : NotebookNode
              nbconvert NotebookNode with definitions resolved
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

    output_list = []
    [output_list.append(x) for x in input_list if x not in output_list]

    return output_list


# --------------------------------------------------------------------------------------------------


def remove_empty_from_list_of_strings(list):

    while ("" in list):
        list.remove("")

    return list


# --------------------------------------------------------------------------------------------------


def string_does_not_contain(disallowed_chars, string_to_check):

    string_does_not_contain_flag = True
    if any(disallowed_char in string_to_check for disallowed_char in disallowed_chars):
        string_does_not_contain_flag = False

    return string_does_not_contain_flag


# --------------------------------------------------------------------------------------------------


def slice_var_from_str(config, datavar, logger):
    if 'slices' in config.keys():
        try:
            datavar = eval("datavar"+config['slices'])
        except IndexError:
            logger.send_message('ABORT', f"IndexError: {config['variable']}" +
                                         f" has dimensions {datavar.shape}" +
                                         f" and input slices string is {config['slices']}")
    return datavar


# --------------------------------------------------------------------------------------------------
