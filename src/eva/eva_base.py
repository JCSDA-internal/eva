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
from eva.utilities.logger import Logger
from eva.utilities.utils import camelcase_to_underscore


# --------------------------------------------------------------------------------------------------


class Config(dict):

    def __init__(self, dict_or_yaml):

        # Program can recieve a dictionary or a yaml file
        if type(dict_or_yaml) is dict:
            config = dict_or_yaml
        else:
            with open(dict_or_yaml, 'r') as ymlfile:
                config = yaml.safe_load(ymlfile)

        # Initialize the parent class with the config
        super().__init__(config)


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
        self.logger.info("  Diagnostic:    " + eva_class_name)
        self.logger.info(" ")

        # Create a configuration object
        # -----------------------------
        self.config = Config(config)

    @abstractmethod
    def execute(self):
        '''
        Each class must implement this method and it is where it will do all of its work.
        '''
        pass


# --------------------------------------------------------------------------------------------------


class EvaFactory():

    def create_eva_object(self, eva_class_name, config, eva_logger):

        # Create temporary logger
        logger = Logger('EvaFactory')

        # Convert capitilized string to one with underscores
        # --------------------------------------------------
        eva_module_name = camelcase_to_underscore(eva_class_name)

        # Check user provided class name against valid tasks
        # --------------------------------------------------
        # List of diagnostics in directory
        valid_diagnostics = os.listdir(os.path.join(return_eva_path(), 'diagnostics'))
        # Remove files like __*
        valid_diagnostics = [vd for vd in valid_diagnostics if '__' not in vd]
        # Remove trailing .py
        valid_diagnostics = [vd.replace(".py", "") for vd in valid_diagnostics]
        # Abort if not found
        if (eva_module_name not in valid_diagnostics):
            logger.abort('Expecting to find a class called in ' + eva_class_name + ' in a file ' +
                         'called ' + os.path.join(return_eva_path(), 'diagnostics', eva_module_name)
                         + '.py but no such file was found.')

        # Import class based on user selected task
        # ----------------------------------------
        try:
            eva_class = getattr(importlib.import_module("eva.diagnostics."+eva_module_name),
                                eva_class_name)
        except Exception as e:
            logger.abort('Expecting to find a class called in ' + eva_class_name + ' in a file ' +
                         'called ' + os.path.join(return_eva_path(), 'diagnostics', eva_module_name)
                         + '.py but no such class was found or an error occurred.')

        # Return implementation of the class (calls base class constructor that is above)
        # -------------------------------------------------------------------------------
        return eva_class(eva_class_name, config, eva_logger)


# --------------------------------------------------------------------------------------------------


def eva(eva_config, eva_logger=None):

    # Create temporary logger
    logger = Logger('EvaSetup')

    # Convert incoming config (either dictionary or file) to dictionary
    if eva_config is dict:
        eva_dict = eva_config
    else:
        # Create dictionary from the input file
        with open(eva_config, 'r') as eva_config_opened:
            eva_dict = yaml.safe_load(eva_config_opened)

    # Get the list of applications
    try:
        diagnostic_configs = eva_dict['diagnostics']
    except KeyError:
        logger.abort('eva configuration must contain \'diagnostics\' and it should provide a ' +
                     'list of diagnostics to be run.')

    # Loop over the applications and run
    for diagnostic_config in diagnostic_configs:

        # Extract name for this diagnostic
        eva_class_name = diagnostic_config['diagnostic name']

        # Create the diagnostic object
        creator = EvaFactory()
        eva_object = creator.create_eva_object(eva_class_name, diagnostic_config, eva_logger)

        # Run the diagnostic
        eva_object.execute()


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
