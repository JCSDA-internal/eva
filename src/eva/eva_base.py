#!/usr/bin/env python

# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# imports
from abc import ABC, abstractmethod
import argparse
import importlib
import os
import sys
import yaml

# local imports
from eva.eva_path import return_eva_path
from eva.utilities.config import Config
from eva.utilities.logger import Logger
from eva.utilities.utils import camelcase_to_underscore, load_yaml_file
from eva.data.data_collections import DataCollections


# --------------------------------------------------------------------------------------------------


class EvaBase(ABC):

    # Base class constructor
    def __init__(self, eva_class_name, config, eva_logger):

        # Replace logger
        # --------------
        if eva_logger is None:
            self.logger = Logger(eva_class_name)
        else:
            self.logger = eva_logger

        self.logger.info("  Initializing eva with the following parameters:")
        self.logger.info("  Class:    " + eva_class_name)
        self.logger.info(" ")

        # Create a configuration object
        # -----------------------------
        self.config = Config(config, self.logger)

    @abstractmethod
    def execute(self, data_collections):
        '''
        Each class must implement this method and it is where it will do all of its work.
        '''
        pass


# --------------------------------------------------------------------------------------------------


class EvaFactory():

    def create_eva_object(self, eva_class_name, eva_group_name, config, eva_logger):

        # Create temporary logger
        logger = Logger('EvaFactory')

        # Convert capitilized string to one with underscores
        # --------------------------------------------------
        eva_module_name = camelcase_to_underscore(eva_class_name)

        # Check user provided class name against valid tasks
        # --------------------------------------------------
        # List of modules in directory
        valid_module = os.listdir(os.path.join(return_eva_path(), eva_group_name))
        # Remove files like __*
        valid_module = [vm for vm in valid_module if '__' not in vm]
        # Remove trailing .py
        valid_module = [vm.replace(".py", "") for vm in valid_module]
        # Abort if not found
        if (eva_module_name not in valid_module):
            logger.abort('Expecting to find a class called in ' + eva_class_name + ' in a file ' +
                         'called ' + os.path.join(return_eva_path(),
                                                  eva_group_name,
                                                  eva_module_name)
                         + '.py but no such file was found.')

        # Import class based on user selected task
        # ----------------------------------------
        try:
            eva_class = getattr(importlib.import_module("eva."+eva_group_name+"."+eva_module_name),
                                eva_class_name)
        except Exception as e:
            logger.abort('Expecting to find a class called in ' + eva_class_name + ' in a file ' +
                         'called ' + os.path.join(return_eva_path(),
                                                  eva_group_name,
                                                  eva_module_name)
                         + '.py but no such class was found or an error occurred.')

        # Return implementation of the class (calls base class constructor that is above)
        # -------------------------------------------------------------------------------
        return eva_class(eva_class_name, config, eva_logger)


# --------------------------------------------------------------------------------------------------


def eva(eva_config, eva_logger=None):

    # Create temporary logger
    logger = Logger('EvaSetup')

    # Convert incoming config (either dictionary or file) to dictionary
    if isinstance(eva_config, dict):
        eva_dict = eva_config
    else:
        # Create dictionary from the input file
        eva_dict = load_yaml_file(eva_config, logger)

    # Get the list of applications
    try:
        diagnostic_configs = eva_dict['diagnostics']
    except KeyError:
        logger.abort('eva configuration must contain \'diagnostics\' and it should provide a ' +
                     'list of diagnostics to be run.')

    if not isinstance(diagnostic_configs, list):
        raise TypeError(f'diagnostics should be a list, it was type: {type(diagnostic_configs)}')

    # Loop over the applications and run
    for diagnostic_config in diagnostic_configs:

        # Each diagnostic should have two dictionaries: data and graphics
        if not all(sub_config in diagnostic_config for sub_config in ['data', 'graphics']):
            msg = "diagnostic config must contain 'data' and 'graphics'"
            raise KeyError(msg)

        # Extract name for this diagnostic data type
        try:
            eva_data_class_name = diagnostic_config['data']['type']
        except Exception as e:
            msg = '\'type\' key not found. \'diagnostic_data_config\': ' \
                  f'{diagnostic_data_config}, error: {e}'
            raise KeyError(msg)

        # Create the data collections
        # ---------------------------
        data_collections = DataCollections()

        # Create the data object
        creator = EvaFactory()
        eva_data_object = creator.create_eva_object(eva_data_class_name,
                                                    'data',
                                                    diagnostic_config['data'],
                                                    eva_logger)

        # Prepare diagnostic data
        eva_data_object.execute(data_collections)

        # Create the figure object
        eva_figure_object = creator.create_eva_object('FigureDriver',
                                                      'plot_tools',
                                                      diagnostic_config,
                                                      eva_logger)

        # Generate figure(s)
        eva_figure_object.execute(data_collections)


# --------------------------------------------------------------------------------------------------


def main():

    # Arguments
    # ---------
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help='Configuration YAML file for driving ' +
                        'the diagnostic. See documentation/examples for how to configure the YAML.')

    # Get the configuation file
    args = parser.parse_args()
    config_file = args.config_file

    assert os.path.exists(config_file), "File " + config_file + " not found"

    # Run the diagnostic(s)
    eva(config_file)


# --------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------------
