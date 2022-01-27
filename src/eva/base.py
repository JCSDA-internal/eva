#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# imports
from abc import ABC, abstractmethod
import click
import importlib
import yaml

# local imports
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
        eva_module_name = camelcase_to_underscore(eva_class_name)

        # Import class based on user selected task
        eva_class = getattr(importlib.import_module("eva."+eva_module_name), eva_class_name)

        # Return implementation of the class (calls base class constructor that is above)
        return eva_class(eva_class_name, config, logger)


# --------------------------------------------------------------------------------------------------


def create_and_run(eva_class_name, config, logger=None):

    '''
    Given a class name and a config this method will create an object of the class name and execute
    the diagnostic defined therein. The config will determine how the diagnostic behaves. The
    config can be passed in using a path to the Yaml file or an already parsed dictionary.

    Args:
        eva_class_name : (str) Name of the class to be instantiated
        config : (str or dictionary) configuation that will guide the diagnostic
    '''

    # Create the diagnostic object
    creator = Factory()
    eva_object = creator.create_object(eva_class_name, config, logger)

    # Execute the diagnostic
    eva_object.execute()


# --------------------------------------------------------------------------------------------------


@click.command()
@click.argument('eva_class_name')
@click.argument('config')
def main(eva_class_name, config):

    """
    Arguments:\n
      EVA_CLASS_NAME: The name of the class (diagnostic) to be instantiated.\n
      CONFIG: Path to a Yaml file containing the configuration for the diagnostic.
    """
    click.echo(eva_class_name)

    create_and_run(eva_class_name, config)


# --------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------------
