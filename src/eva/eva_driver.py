# (C) Copyright 2021-2023 NOAA/NWS/EMC
#
# (C) Copyright 2021-2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime
import argparse
import os
from collections import defaultdict
import xarray as xr
import numpy as np

from eva.utilities.config import get
from eva.utilities.logger import Logger
from eva.utilities.timing import Timing
from eva.data.data_driver import data_driver
from eva.time_series.time_series import add_empty_to_timeseries
from eva.time_series.time_series import collapse_collection_to_time_series
from eva.time_series.time_series_utils import create_empty_data, get_filename, check_file
from eva.transforms.transform_driver import transform_driver
from eva.plotting.batch.base.plot_tools.figure_driver import figure_driver
from eva.data.data_collections import DataCollections
from eva.utilities.duration import iso_duration_to_timedelta
from eva.utilities.utils import load_yaml_file

# --------------------------------------------------------------------------------------------------


def read_transform(logger, timing, eva_dict, data_collections):

    """
    Read the data and perform any transforms based on the configuration.

    Parameters:
        logger (Logger): An instance of the logger for logging messages.
        timing (Timing): An instance of the timing object for timing the process.
        eva_dict (dict): The configuration dictionary for the EVA process.
        data_collections (DataCollections): An instance of the data collections object.

    Returns:
        None
    """

    # Get the datasets configuration
    datasets_config = get(eva_dict, logger, 'datasets')

    # Optionally suppress the display of the collection
    suppress_collection_display = get(eva_dict, logger, 'suppress_collection_display', False)

    # Loop over datasets reading each one in turn, internally appending the data_collections
    for dataset_config in datasets_config:

        # Prepare diagnostic data
        logger.info('Running data driver')
        timing.start('DataDriverExecute')
        data_driver(dataset_config, data_collections, timing, logger)
        timing.stop('DataDriverExecute')

    # After reading all datasets display the collection
    if not suppress_collection_display:
        logger.info('Reading of Eva data complete: status of collections: ')
        data_collections.display_collections()

    # Perform any transforms
    if 'transforms' in eva_dict:
        logger.info(f'Running transform driver')
        timing.start('TransformDriverExecute')
        transform_driver(eva_dict, data_collections, timing, logger)
        timing.stop('TransformDriverExecute')

        # After reading all datasets display the collection
        if not suppress_collection_display:
            logger.info('Transformations of data complete: status of collections: ')
            data_collections.display_collections()


# --------------------------------------------------------------------------------------------------


def read_transform_time_series(logger, timing, eva_dict, data_collections):

    """
    Read the data and perform transforms on the fly. Then collapse data into time series

    Parameters:
        logger (Logger): An instance of the logger for logging messages.
        timing (Timing): An instance of the timing object for timing the process.
        eva_dict (dict): The configuration dictionary for the EVA process.
        data_collections (DataCollections): An instance of the data collections object.

    Returns:
        None
    """

    # Iterate through list of time series dictionaries
    for time_series_config in eva_dict['time_series']:

        # Check for required keys
        # -----------------------
        required_keys = [
            'begin_date',
            'final_date',
            'interval',
            'collection',
            'variables',
            ]
        for key in required_keys:
            logger.assert_abort(key in time_series_config, 'If running Eva in time series ' +
                                f'mode the time series config must contain "{key}"')

        # Write message that this is a time series run
        logger.info('This instance of Eva is being used to accumulate a time series.')

        # Optionally suppress the display of the collection
        suppress_collection_display = get(eva_dict, logger, 'suppress_collection_display', False)

        # Extract the dates of the time series
        begin_date = time_series_config['begin_date']
        final_date = time_series_config['final_date']
        interval = time_series_config['interval']

        # Convert begin and end dates from ISO strings to datetime objects
        begin_date = datetime.fromisoformat(begin_date)
        final_date = datetime.fromisoformat(final_date)

        # Convert interval ISO string to timedelta object
        interval = iso_duration_to_timedelta(logger, interval)

        # Make list of dates from begin to end with interval
        dates = []
        date = begin_date
        count = 0
        while date <= final_date:
            dates.append(date)
            date += interval
            count += 1
            # Abort if count hits one million
            logger.assert_abort(count < 1e6, 'You are planning to read more than one million ' +
                                'time steps. This is likely an error. Please check your ' +
                                'configuration.')

        # Get all datasets configuration
        all_datasets = get(eva_dict, logger, 'datasets')

        # Find all dataset_configs with collection name
        datasets_config = []
        for dataset in all_datasets:
            if dataset['name'] == time_series_config["collection"]:
                datasets_config.append(dataset)

        # Save transforms to transform_dict based on collection
        transform_dict = defaultdict(list)
        if 'transforms' in eva_dict:
            for transform in get(eva_dict, logger, 'transforms'):
                # Get collection name
                name = transform['new name'].split('::')[0]
                if name == time_series_config['collection']:
                    transform_dict['transforms'].append(transform)

        # Check if first file is empty. If it is, abort.
        empty_dataset_config = datasets_config[0]
        filename = get_filename(empty_dataset_config, logger)
        check_file(filename, logger)

        # Loop over datasets reading each one in turn, internally appending the data_collections
        for ind, dataset_config in enumerate(datasets_config):

            # Pull out information to check for missing date
            date = dates[ind]

            # Check if file exists, if not add empty and continue
            filename = get_filename(dataset_config, logger)
            if not os.path.isfile(filename):
                add_empty_to_timeseries(logger, date, ind, timing, time_series_config,
                                        empty_dataset_config, data_collections)
                continue
            # Check if file exists but is size zero, add empty and continue
            elif os.stat(filename).st_size == 0:
                add_empty_to_timeseries(logger, date, ind, timing, time_series_config,
                                        empty_dataset_config, data_collections)
                continue

            # Create a temporary collection for this time step
            data_collections_tmp = DataCollections()

            # Prepare diagnostic data
            logger.info('Running data driver')
            timing.start('DataDriverExecute')
            data_driver(dataset_config, data_collections_tmp, timing, logger)
            timing.stop('DataDriverExecute')

            # Perform any transforms on the fly
            if transform_dict:
                logger.info(f'Running transform driver')
                timing.start('TransformDriverExecute')
                transform_driver(transform_dict, data_collections_tmp, timing, logger)
                timing.stop('TransformDriverExecute')

            # Collapse data into time series
            collapse_collection_to_time_series(logger, ind, date, time_series_config,
                                               data_collections, data_collections_tmp)

        if not suppress_collection_display:
            logger.info('Computing of Eva time series complete: status of collection:')
            data_collections.display_collections()


# --------------------------------------------------------------------------------------------------


def eva(eva_config, eva_logger=None):

    """
    Execute the Evaluation and Visualization Analysis (EVA) process based on the provided
    configuration.

    Parameters:
        eva_config (dict or str): Configuration data for the EVA process. It can be a dictionary or
        the path to a YAML configuration file.
        eva_logger (Logger, optional): An instance of the logger for logging messages. Default is
        None.

    Returns:
        None
    """

    # Create timing object
    timing = Timing()

    # Create temporary logger
    logger = Logger('EvaSetup')

    logger.info('Starting Eva')

    # Convert incoming config (either dictionary or file) to dictionary
    # -----------------------------------------------------------------
    timing.start('Generate Dictionary')
    if isinstance(eva_config, dict):
        eva_dict = eva_config
    else:
        # Create dictionary from the input file
        eva_dict = load_yaml_file(eva_config, logger)
    timing.stop('Generate Dictionary')

    # Each diagnostic should have two dictionaries: data and graphics
    # ---------------------------------------------------------------
    if not all(sub_config in eva_dict for sub_config in ['datasets', 'graphics']):
        logger.abort("The configuration must contain 'datasets' and 'graphics' keys.")

    # Create the data collections
    # ---------------------------
    data_collections = DataCollections('time_series' in eva_dict)

    # Check to see if this a time series run of eva and then read and transform
    # -------------------------------------------------------------------------
    if 'time_series' in eva_dict:
        read_transform_time_series(logger, timing, eva_dict, data_collections)
    else:
        read_transform(logger, timing, eva_dict, data_collections)

    # Generate figure(s)
    # ------------------
    logger.info(f'Running figure driver')
    timing.start('FigureDriverExecute')
    figure_driver(eva_dict, data_collections, timing, logger)
    timing.stop('FigureDriverExecute')

    timing.finalize()


# --------------------------------------------------------------------------------------------------


def main():

    """
    Entry point for main eva program. Reads configuration from a YAML file and executes eva
    based on what is described in the configuration file.

    Parameters:
        config_file (str): The path to the configuration YAML file.

    Returns:
        None
    """

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
