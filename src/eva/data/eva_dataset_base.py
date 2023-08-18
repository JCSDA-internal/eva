# (C) Copyright 2021-2023 NOAA/NWS/EMC
#
# (C) Copyright 2021-2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# imports
from abc import ABC, abstractmethod
import importlib
import os
import sys
import yaml

# local imports
from eva.eva_path import return_eva_path
from eva.utilities.config import Config
from eva.utilities.logger import Logger
from eva.utilities.timing import Timing
from eva.utilities.utils import camelcase_to_underscore
from eva.data.data_collections import DataCollections


# --------------------------------------------------------------------------------------------------


class EvaDatasetBase(ABC):

    """Abstract base class for EVA dataset objects."""

    # Base class constructor
    def __init__(self, eva_class_name, eva_logger, timing):

        """
        Initialize the base class for eva dataset objects.

        Args:
            eva_class_name (str): Name of the eva class to instantiate.
            eva_logger (Logger): Logger instance for logging messages.
            timing (Timing): Timing instance for performance measurement.

        """

        # Replace logger
        # --------------
        if eva_logger is None:
            self.logger = Logger(eva_class_name)
        else:
            self.logger = eva_logger

        # Store name
        # ----------
        self.name = eva_class_name

        # Write object initialization message
        # -----------------------------------
        self.logger.info(f"  Initializing eva {self.name} object")

    @abstractmethod
    def execute(self, config, data_collections, timing):

        """
        Execute the dataset processing.

        Args:
            config (dict): Configuration settings for dataset processing.
            data_collections (DataCollections): Instance of the DataCollections class.
            timing (Timing): Timing instance for performance measurement.
        """

        pass

    @abstractmethod
    def generate_default_config(self, filenames, collection_name, control_file=None):

        """
        Generate the default configuration for the dataset.

        Args:
            filenames (list): List of filenames associated with the dataset.
            collection_name (str): Name of the collection.
            control_file (str): Path to the control file (optional).
        """

        pass

# --------------------------------------------------------------------------------------------------


class EvaDatasetFactory():

    """Factory class for creating eva data ingest objects."""

    def create_eva_object(self, eva_class_name, eva_group_name, eva_logger, timing):

        """
        Create an eva dataset ingest object.

        Args:
            eva_class_name (str): Name of the EVA class.
            eva_group_name (str): Name of the EVA group.
            eva_logger (Logger): Logger instance for logging messages.
            timing (Timing): Timing instance for performance measurement.

        Returns:
            EvaDatasetBase: An instance of the specified EVA dataset class.
        """

        # Create temporary logger
        logger = Logger('EvaDatasetFactory')

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
        expected_file = os.path.join(return_eva_path(), eva_group_name, eva_module_name)
        if (eva_module_name not in valid_module):
            logger.abort(f'Expecting to find a class called \'{eva_class_name}\' in a file ' +
                         f'called \'{expected_file}.py\' but no such file was found.')

        # Import class based on user selected task
        # ----------------------------------------
        module_to_import = "eva."+eva_group_name+"."+eva_module_name
        timing.start(f'EvaDatasetFactory import: {eva_class_name} from {module_to_import}')
        try:
            eva_class = getattr(importlib.import_module(module_to_import), eva_class_name)
        except Exception as e:
            logger.abort(f'Expecting to find a class called \'{eva_class_name}\' in a file ' +
                         f'called \'{expected_file}.py\' but no such file was found or an error ' +
                         f'occurred during import. \n Reported error: {e}.')
        timing.stop(f'EvaDatasetFactory import: {eva_class_name} from {module_to_import}')

        # Return implementation of the class (calls base class constructor that is above)
        # -------------------------------------------------------------------------------
        return eva_class(eva_class_name, eva_logger, timing)
