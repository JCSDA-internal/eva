# (C) Copyright 2024- NOAA/NWS/EMC
#
# (C) Copyright 2024- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import numpy as np
import xarray as xr
from eva.data.data_collections import DataCollections
from eva.time_series.time_series_utils import create_empty_data

# --------------------------------------------------------------------------------------------------


xr_aggregation_methods = {
    'mean': lambda ds, dim: ds.mean(dim=dim, skipna=True),
    'sum': lambda ds, dim: ds.sum(dim=dim, skipna=True),
}


# --------------------------------------------------------------------------------------------------

def add_empty_to_timeseries(logger, date, ind, timing, time_series_config,
                            dataset_config, data_collections):

    ''' Add empty collection to timeseries for missing date  '''
    empty_data_collection = create_empty_data(time_series_config, dataset_config, timing, logger)
    collapse_collection_to_time_series(logger, ind, date, time_series_config, data_collections,
                                       empty_data_collection)


# --------------------------------------------------------------------------------------------------


def collapse_collection_to_time_series(logger, ind, date, time_series_config, data_collections,
                                       data_collections_tmp):

    # Parse the configuration
    # -----------------------

    # Collection
    collection_to_ts = time_series_config['collection']

    # Variables
    var_to_ts = time_series_config['variables']

    # Optional: aggregation methods
    aggregation_methods = time_series_config.get('aggregation_methods', [])

    # If specifying aggregation methods it must be accompanied by a dimension
    if aggregation_methods:
        logger.assert_abort('dimension' in time_series_config, 'When specifying aggregation '
                            'methods a dimension must also be specified.')
        dimension = time_series_config['dimension']

    # Get the actual dataset for this step in the time series
    # -------------------------------------------------------
    dataset_tmp = data_collections_tmp.get_data_collection(collection_to_ts)

    # Remove any variables that are not to be aggregated
    if var_to_ts != ['all']:
        variables_to_remove = [var for var in list(dataset_tmp.data_vars) if var not in var_to_ts]
        dataset_tmp = dataset_tmp.drop_vars(variables_to_remove)

    # Create an empty dataset to hold the aggregated data
    # ---------------------------------------------------
    dataset_aggregated = xr.Dataset()

    # If there is no aggregation method specified, just add the dataset to the time series
    if not aggregation_methods:
        dataset_aggregated = xr.merge([dataset_aggregated, dataset_tmp])
    else:
        for aggregation_method in aggregation_methods:
            # Assert that aggregation_method is in the aggregation methods
            logger.assert_abort(aggregation_method in xr_aggregation_methods,
                                f'Unknown aggregation method {aggregation_method}')

            # Compute the aggregation_method
            dataset_am = xr_aggregation_methods[aggregation_method](dataset_tmp, dim=dimension)

            # Append each variable name in dataset_am with _aggregation_method
            rename_dict = {var: f"{var}_{aggregation_method}" for var in dataset_am.data_vars}
            dataset_am = dataset_am.rename(rename_dict)

            # Merge all the results into the aggregated dataset
            dataset_aggregated = xr.merge([dataset_aggregated, dataset_am])

    # Get all dims of dataset_aggregated and create empty array with those dims
    # -------------------------------------------------------------------------
    dims = {dim: dataset_aggregated.sizes[dim] for dim in dataset_aggregated.dims}
    data_array_shape = tuple(dims[dim] for dim in dims)
    dataset_aggregated['MetaData::Dates'] = xr.DataArray(np.full(data_array_shape, date),
                                                         dims=dataset_aggregated.dims)

    # Add the time index to the aggregated dataset
    # --------------------------------------------
    dataset_aggregated = dataset_aggregated.expand_dims('TimeIndex')
    dataset_aggregated['TimeIndex'] = [0]

    # Append the dataset with the aggregation
    concat_dimension = 'TimeIndex' if ind > 0 else None
    data_collections.create_or_add_to_collection(f'{collection_to_ts}_time_series',
                                                 dataset_aggregated, concat_dimension)


# --------------------------------------------------------------------------------------------------
