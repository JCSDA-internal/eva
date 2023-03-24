#!/usr/bin/env python

# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

# imports
import argparse
import os

# local imports
from eva.eva_path import return_eva_path
from eva.utilities.logger import Logger, textcolors
from eva.utilities.utils import load_yaml_file, replace_vars_dict, replace_vars_notebook
from eva.plot_tools import figure_driver
from eva.plot_tools.figure_driver import FigureDriver

# --------------------------------------------------------------------------------------------------


def application_tests(logger):

    from eva.eva_base import eva

    # Write some messaging
    logger.info(f'Running Eva application tests ...')

    # Path to eva install
    eva_path = return_eva_path()

    # List of testing files
    tests = os.listdir(os.path.join(eva_path, 'tests', 'config'))

    # Create dictionary that contains overwrite
    overwrite_dict = {}
    overwrite_dict['data_input_path'] = os.path.join(eva_path, 'tests', 'data')

    # Loop over tests, populate YAML and run test
    for test in tests:

        # Write some information
        logger.info(f'{textcolors.green}Running Eva application test with {test}{textcolors.end}')

        # Load the raw config into dictionary
        test_config = load_yaml_file(os.path.join(eva_path, 'tests', 'config', test), logger)

        # Replace templated variables using values from the overwrite dictionary
        test_config = replace_vars_dict(test_config, **overwrite_dict)

        # Run Eva with that config
        eva(test_config)


def notebook_tests(logger):

    from eva.eva_base import eva
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor

    # Write some messaging
    logger.info(f'Running Eva notebook tests ...')

    # Path to eva install
    eva_path = return_eva_path()

    # List of notebooks
    notebooks = os.listdir(os.path.join(eva_path, 'tests', 'notebooks'))

    # Create dictionary that contains overwrite
    overwrite_dict = {}
    overwrite_dict['data_input_path'] = os.path.join(eva_path, 'tests', 'data')

    # Loop over tests, populate YAML and run test
    for notebook in notebooks:

        # Write some information
        logger.info(f'{textcolors.green}Running Eva notebook test with {notebook}{textcolors.end}')

        # Open notebook using nbconvert
        with open(os.path.join(eva_path, 'tests', 'notebooks', notebook)) as file:
            nb_in = nbformat.read(file, nbformat.NO_CONVERT)

        # Replace variables in notebook
        updated_nb_in = replace_vars_notebook(nb_in, **overwrite_dict)

        # Execute notebook
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        nb_out = ep.preprocess(updated_nb_in)

        # Log completion
        logger.info(f'{textcolors.green}Completed Eva notebook test' +
                    f' with {notebook}{textcolors.end}')

# --------------------------------------------------------------------------------------------------


def main():

    # Parse arguments
    # ---------------
    parser = argparse.ArgumentParser()
    parser.add_argument('test_type', type=str, help='Test type to run: unit, application etc.')

    args = parser.parse_args()
    test_type = args.test_type

    # Create a logger for writing info
    # --------------------------------
    logger = Logger('Eva test suite')

    # Check for valid test type
    # -------------------------
    test_type = test_type.lower()  # Convert to always be lower case
    valid_test_types = ['application', 'notebook']
    if test_type not in valid_test_types:
        logger.abort(f'Requested test \'{test_type}\' is not valid. Options are {valid_test_types}')

    # Run the application tests
    # -------------------------
    if test_type == 'application':
        application_tests(logger)
    if test_type == 'notebook':
        notebook_tests(logger)

# --------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------------
