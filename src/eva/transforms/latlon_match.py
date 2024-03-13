# (C) Copyright 2024 NOAA/NWS/EMC 
#
#(C) Copyright 2024 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from xarray import Dataset, DataArray
from eva.utilities.config import get
from eva.utilities.logger import Logger
from eva.transforms.transform_utils import parse_for_dict, split_collectiongroupvariable

def latlon_match(config, data_collections):

    # Create a logger
    logger = Logger('LatLonMatchTransform')

    # Parse the for dictionary
    _, _, variables = parse_for_dict(config, logger)

    # Parse config for names
    starting_dataset_name = get(config, logger, 'dataset_to_modify')
    starting_latlon_name = get(config, logger, 'starting_latlon')
    match_to_latlon_name = get(config, logger, 'match_latlon_to')

    # Extract collection and group
    cgv = split_collectiongroupvariable(logger, starting_dataset_name)

    # Retrieve collections using collection names 
    starting_lat = data_collections.get_variable_data_array(starting_latlon_name, 'MetaData', 'latitude').to_numpy()
    starting_lon = data_collections.get_variable_data_array(starting_latlon_name, 'MetaData', 'longitude').to_numpy()
    match_to_lat = data_collections.get_variable_data_array(match_to_latlon_name, 'MetaData', 'latitude').to_numpy()
    match_to_lon = data_collections.get_variable_data_array(match_to_latlon_name, 'MetaData', 'longitude').to_numpy()

    # Find matching index (use optimized way with dask if possible
    matching_index = []
    for i in range(len(starting_lat)):
        matching_index.append((abs(match_to_lat - starting_lat[i]) + abs(match_to_lon - starting_lon[i])).argmin())

    # Loop through starting_dataset and update all variable arrays
    update_ds_list = []
    for variable in variables:
        var_array = data_collections.get_variable_data_array(cgv[0], cgv[1], variable)
        #dims = list(var_array.dims)

        # Index var_array based on matching_index into new numpy array
        var_values = var_array.values
        var_values = var_values[matching_index]

        # Create new ds in the way that data readers do

        # Add new array to update_ds
        
    # merge all the datasets    
    # Save new array in place using new data set
    # Or instead of saving in place, just add to new collection with new collection name
    # may need to create a method in data_collections to do an inplace update

