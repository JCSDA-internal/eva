# (C) Copyright 2021-2023 NOAA/NWS/EMC
#
# (C) Copyright 2021-2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from eva.utilities.logger import Logger
from eva.utilities.timing import Timing
from eva.data.data_driver import data_driver
from eva.transforms.transform_driver import transform_driver
from eva.plot_tools.figure_driver import figure_driver
from eva.data.data_collections import DataCollections
from eva.utilities.utils import load_yaml_file
import argparse
import os

def eva(eva_config, eva_logger=None):

    # Create timing object
    timing = Timing()

    # Create temporary logger
    logger = Logger('EvaSetup')

    logger.info('Starting Eva')

    # Convert incoming config (either dictionary or file) to dictionary
    timing.start('Generate Dictionary')
    if isinstance(eva_config, dict):
        eva_dict = eva_config
    else:
        # Create dictionary from the input file
        eva_dict = load_yaml_file(eva_config, logger)
    timing.stop('Generate Dictionary')

    # Each diagnostic should have two dictionaries: data and graphics
    if not all(sub_config in eva_dict for sub_config in ['datasets', 'graphics']):
        msg = "diagnostic config must contain 'datasets' and 'graphics'"
        raise KeyError(msg)

    # Create the data collections
    # ---------------------------
    data_collections = DataCollections()

    # Prepare diagnostic data
    logger.info(f'Running data driver')
    timing.start('DataDriverExecute')
    data_driver(eva_dict, data_collections, timing, logger)
    timing.stop('DataDriverExecute')

    # Create the transforms
    if 'transforms' in eva_dict:
        logger.info(f'Running transform driver')
        timing.start('TransformDriverExecute')
        transform_driver(eva_dict, data_collections, timing, logger)
        timing.stop('TransformDriverExecute')

    # Generate figure(s)
    logger.info(f'Running figure driver')
    timing.start('FigureDriverExecute')
    figure_driver(eva_dict, data_collections, timing, logger)
    timing.stop('FigureDriverExecute')

    timing.finalize()


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
