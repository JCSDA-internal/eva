import os
import numpy as np
import xarray as xr
from eva.data.data_driver import data_driver
from eva.data.data_collections import DataCollections


filename_retrieval = {
    "IodaObsSpace": lambda dataset_config: dataset_config["filenames"],
    "JediVariationalBiasCorrection": lambda dataset_config: dataset_config["bias_file"],
}


def update_filename(dataset_config, filename, logger):
    """ Update the filename associated with a dataset_config """
    match dataset_config['type']:
        case 'IodaObsSpace':
            dataset_config['filenames'] = [filename]
        case 'JediVariationalBiasCorrection':
            dataset_config['bias_file'] = filename
        case _:
            logger.abort(f'Unknown dataset_type {dataset_type} in update_filename')

    return dataset_config


def get_filenames(dataset_config, logger):
    """ Retrieve filenames using given type  """

    dataset_type = dataset_config["type"]
    logger.assert_abort(dataset_type in filename_retrieval,
                        f'Unknown dataset_type {dataset_type}')
    filenames = filename_retrieval[dataset_type](dataset_config)

    # Ensure filenames is always a list, handling None as an empty list
    if filenames is None:
        return []
    return filenames if isinstance(filenames, list) else [filenames]


def check_file(filename, logger):
    """ Check if first file exists and is nonzero  """

    if not os.path.isfile(filename):
        logger.abort('First file provided to timeseries must exist.')
    elif os.stat(filename).st_size == 0:
        logger.abort('First file provided to timeseries must be nonzero.')


def create_empty_data(timeseries_config, dataset_config, timing, logger):
    """ Creating an empty data collection to use for missing cycle times  """

    dc_tmp = DataCollections()
    collection = timeseries_config["collection"]
    data_driver(dataset_config, dc_tmp, timing, logger)
    dataset = dc_tmp.get_data_collection(collection)
    empty_data = xr.full_like(dataset, np.nan)
    dc = DataCollections()
    dc.create_or_add_to_collection(collection, empty_data)
    return dc
