# (C) Copyright 2021-2023 NOAA/NWS/EMC
#
# (C) Copyright 2021-2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import pandas as pd
import hvplot.pandas
import geopandas as gpd
from eva.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def make_dataframe(dc_dict, plot_list, ch_required_dict, logger):

    """
    Create a Pandas DataFrame containing data for the specified plot items.

    Parameters:
        dc_dict (dict): A dictionary containing data collections.
        plot_list (list): A list of plot items in the format "collection::group::variable" or
        "collection::group::variable::channel".
        ch_required_dict (dict): A dictionary indicating whether a channel number is required for
        each collection.
        logger (Logger): An instance of the logger for logging messages.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the collected data.
    """

    df = pd.DataFrame()

    for item in plot_list:
        item_list = item.split('::')
        if len(item_list) == 3:
            collection = item_list[0]
            group = item_list[1]
            variable = item_list[2]
            if ch_required_dict[collection] is True:
                logger.abort(f'Please include channel number for \'{item}\'.')

            arr = dc_dict[collection].get_variable_data(collection,
                                                        group,
                                                        variable)
        elif len(item_list) == 4:
            collection = item_list[0]
            group = item_list[1]
            variable = item_list[2]
            channel = int(item_list[3])
            arr = dc_dict[collection].get_variable_data(collection,
                                                        group,
                                                        variable,
                                                        channel)
        else:
            logger.abort(f'Insufficient info in \'{item}\'.')
        df[item] = arr

    df = df.dropna()
    return df


# --------------------------------------------------------------------------------------------------


def hvplot_line_plot(dc_dict, plot_list, ch_required_dict, logger):

    """
    Create and return an interactive line plot using the collected data.

    Parameters:
        dc_dict (dict): A dictionary containing data collections.
        plot_list (list): A list of plot items in the format "collection::group::variable" or
        "collection::group::variable::channel".
        ch_required_dict (dict): A dictionary indicating whether a channel number is required for
        each collection.
        logger (Logger): An instance of the logger for logging messages.

    Returns:
        hvplot: An interactive line plot.
    """

    df = make_dataframe(dc_dict, plot_list, ch_required_dict, logger)
    return df.hvplot.line()

# --------------------------------------------------------------------------------------------------


def hvplot_histogram(dc_dict, plot_list, ch_required_dict, logger):

    """
    Create and return an interactive histogram plot using the collected data.

    Parameters:
        dc_dict (dict): A dictionary containing data collections.
        plot_list (list): A list of plot items in the format "collection::group::variable" or
        "collection::group::variable::channel".
        ch_required_dict (dict): A dictionary indicating whether a channel number is required for
        each collection.
        logger (Logger): An instance of the logger for logging messages.

    Returns:
        hvplot: An interactive histogram plot.
    """

    df = make_dataframe(dc_dict, plot_list, ch_required_dict, logger)
    return df.hvplot.hist(bins=100)

# --------------------------------------------------------------------------------------------------


def hvplot_map_scatter(dc_dict, plot_entry, logger):

    """
    Create and return an interactive map scatter plot using latitude, longitude, and a specified
    variable.

    Parameters:
        dc_dict (dict): A dictionary containing data collections.
        plot_entry (str): A plot item in the format "collection::group::variable".
        logger (Logger): An instance of the logger for logging messages.

    Returns:
        hvplot: An interactive map scatter plot.
    """

    df = pd.DataFrame()
    collection, group, variable = plot_entry.split('::')
    df['Latitude'] = dc_dict[collection].get_variable_data(collection,
                                                           'MetaData',
                                                           'latitude')
    df['Longitude'] = dc_dict[collection].get_variable_data(collection,
                                                            'MetaData',
                                                            'longitude')
    df[variable] = dc_dict[collection].get_variable_data(collection,
                                                         group,
                                                         variable)
    df = df.dropna()
    gdf = gpd.GeoDataFrame(
        df[variable], geometry=gpd.points_from_xy(x=df.Longitude, y=df.Latitude)
    )
    return gdf.hvplot(global_extent=True,
                      geo=True, tiles='OSM',
                      hover_cols=variable, frame_width=700)

# --------------------------------------------------------------------------------------------------


def hvplot_density_plot(dc_dict, plot_list, ch_required_dict, logger):

    """
    Create and return an interactive density plot using the collected data.

    Parameters:
        dc_dict (dict): A dictionary containing data collections.
        plot_list (list): A list of plot items in the format "collection::group::variable" or
        "collection::group::variable::channel".
        ch_required_dict (dict): A dictionary indicating whether a channel number is required for
        each collection.
        logger (Logger): An instance of the logger for logging messages.

    Returns:
        hvplot: An interactive density plot.
    """

    df = make_dataframe(dc_dict, plot_list, ch_required_dict, logger)
    return df.hvplot.kde(filled=True, legend='top_left', alpha=0.5, bandwidth=0.1, height=400)

# --------------------------------------------------------------------------------------------------


def hvplot_scatter(dc_dict, x, y, ch_required_dict, logger):

    """
    Create and return an interactive scatter plot using the collected data.

    Parameters:
        dc_dict (dict): A dictionary containing data collections.
        x (str): The variable for the x-axis.
        y (str): The variable for the y-axis.
        ch_required_dict (dict): A dictionary indicating whether a channel number is required for
        each collection.
        logger (Logger): An instance of the logger for logging messages.

    Returns:
        hvplot: An interactive scatter plot.
    """

    plot_list = [x, y]
    df = make_dataframe(dc_dict, plot_list, ch_required_dict, logger)
    return df.hvplot.scatter(x, y, s=20, c='b', height=400, width=400)

# --------------------------------------------------------------------------------------------------
