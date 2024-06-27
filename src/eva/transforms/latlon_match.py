# (C) Copyright 2024 NOAA/NWS/EMC
#
# (C) Copyright 2024 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import numpy as np
from xarray import Dataset, DataArray
from eva.utilities.config import get
from eva.utilities.logger import Logger
from eva.transforms.transform_utils import parse_for_dict, split_collectiongroupvariable


def latlon_match(config, data_collections):

    """
    Applies lat/lon match transform to a given collection.

    Args:
        config (dict): A configuration dictionary containing transformation parameters.
        data_collections (DataCollections): An instance of the DataCollections class containing
        input data.

    Returns:
        None

    This function applies lat/lon matching to variables in the base collection. A new collection
    with matched variables is added to the data collection.

    base collection: collection to perform the latlon matching on
    base_latlon: the collection with lat/lon coordiates corresponding to base collection
    match_base_latlon_to: the collection with lat/lon coordinates corresponding to what you want to
    match the base latlon to.

    """

    # Create a logger
    logger = Logger('LatLonMatchTransform')

    # Parse the for dictionary
    _, _, variables = parse_for_dict(config, logger)

    # Parse config for names
    base_collection = get(config, logger, 'base_collection')
    base_latlon_name = get(config, logger, 'base_latlon')
    match_latlon_name = get(config, logger, 'match_base_latlon_to')

    # Extract collection and group
    cgv = split_collectiongroupvariable(logger, base_collection)

    # Retrieve collections using collection names
    base_lat = data_collections.get_variable_data_array(base_latlon_name, 'MetaData',
                                                        'latitude').to_numpy()
    base_lon = data_collections.get_variable_data_array(base_latlon_name, 'MetaData',
                                                        'longitude').to_numpy()
    match_lat = data_collections.get_variable_data_array(match_latlon_name, 'MetaData',
                                                         'latitude').to_numpy()
    match_lon = data_collections.get_variable_data_array(match_latlon_name, 'MetaData',
                                                         'longitude').to_numpy()

    # Find matching index (this can be updated using dask)
    matching_index = []
    for i in range(len(base_lat)):
        matching_index.append((abs(base_lat - match_lat[i]) +
                               abs(base_lon - match_lon[i])).argmin())

    # Retrieve data collection from data collections
    match_ds = data_collections.get_data_collection(cgv[0])

    # Loop through starting_dataset and update all variable arrays
    update_ds_list = []
    for variable in variables:
        var_array = data_collections.get_variable_data_array(cgv[0], cgv[1], variable)
        var_values = var_array.values

        # Index data array with matching_index and then save to new collection
        var_values = var_values[matching_index]
        var_array.values = var_values
        match_ds[f'{cgv[1]}::{variable}'] = var_array

    # get new collection name
    new_collection_name = get(config, logger, 'new_collection_name')

    # add new collection to data collections
    data_collections.create_or_add_to_collection(new_collection_name, match_ds)
    match_ds.close()
