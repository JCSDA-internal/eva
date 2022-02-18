#!/usr/bin/env python

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


class Base(ABC):

    # Base class constructor
    def __init__(self, eva_class_name, config, logger):

        print("\nInitializing eva with the following parameters:")
        print("  Diagnostic:    ", eva_class_name)
        print("  Configuration: ", config)

        # Create message logger
        # ---------------------
        if logger is None:
            self.logger = Logger(eva_class_name)
        else:
            self.logger = logger

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


class Factory():

    def create_object(self, eva_class_name, config, logger):

        # Convert capitilized string to one with underscores
        # --------------------------------------------------
        eva_module_name = camelcase_to_underscore(eva_class_name)

        # Check user provided class name against valid tasks
        # --------------------------------------------------
        # List of diagnostics in directory
        valid_diagnostics = os.listdir(os.path.join(return_eva_path(), 'diagnostics'))
        # Remove files like __*
        valid_diagnostics = [ vd for vd in valid_diagnostics if '__' not in vd ]
        # Remove trailing .py
        valid_diagnostics = [vd.replace(".py", "") for vd in valid_diagnostics]
        # Abort if not found
        if (eva_module_name not in valid_diagnostics):
            logger.abort('No module found that matches the class name ' + eva_class_name + '. ' +
                         'Expecting to find a class called in ' + eva_class_name + 'in a file ' +
                         'called ' + os.path.join(return_eva_path(), 'diagnostics', eva_module_name))

        # Import class based on user selected task
        # ----------------------------------------
        try:
            eva_class = getattr(importlib.import_module("eva.diagnostics."+eva_module_name),
                                eva_class_name)
        except Exception:
            logger.abort('Expecting to find a class called in ' + eva_class_name + 'in a file ' +
                         'called ' + os.path.join(return_eva_path(), 'diagnostics',
                         eva_module_name) + ' but something went wrong attempting to import it.')

        # Return implementation of the class (calls base class constructor that is above)
        # -------------------------------------------------------------------------------
        return eva_class(eva_class_name, config, logger)


# --------------------------------------------------------------------------------------------------


def eva(eva_config, logger):

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
    except Exception:
        logger.abort('eva configuration must contain \'diagnostics\' and it should provide a ' +
                     'list of diagnostics to be run.')

    # Loop over the applications and run
    for diagnostic_config in diagnostic_configs:

        # Extract name for this diagnostic
        eva_class_name = diagnostic_config['diagnostic name']

        # Create the diagnostic object
        creator = Factory()
        eva_object = creator.create_object(eva_class_name, diagnostic_config, logger)


# --------------------------------------------------------------------------------------------------


def main():

    # Arguments
    # ---------
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help='Configuration YAML file for driving ' +
                        'the diagnostic. See documentation/examples for how to configure the YAML.')

    # Create temporary logger
    logger = Logger('EvaSetup')

    # Get the configuation file
    args = parser.parse_args()
    config_file = args.config_file

    assert os.path.exists(config_file), "File " + config_file + " not found"

    # Run the diagnostic(s)
    eva(config_file, logger)


# --------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------------
