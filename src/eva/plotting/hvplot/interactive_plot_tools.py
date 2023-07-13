import pandas as pd
import hvplot.pandas
import geopandas as gpd


def make_dataframe(dc_dict, plot_list, ch_required_dict, logger):
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

def hvplot_line_plot(dc_dict, plot_list, ch_required_dict, logger):
    df = make_dataframe(dc_dict, plot_list, ch_required_dict, logger)
    return df.hvplot.line()

# --------------------------------------------------------------------------------------------------


def hvplot_histogram(dc_dict, plot_list, ch_required_dict, logger):
    df = make_dataframe(dc_dict, plot_list, ch_required_dict, logger)
    return df.hvplot.hist(bins=100)

# --------------------------------------------------------------------------------------------------


def hvplot_map_scatter(dc_dict, plot_entry, logger):
    # retrieve latitude, longitude, and variable
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
    df = make_dataframe(dc_dict, plot_list, ch_required_dict, logger)
    return df.hvplot.kde(filled=True, legend='top_left', alpha=0.5, bandwidth=0.1, height=400)

# --------------------------------------------------------------------------------------------------


def hvplot_scatter(dc_dict, x, y, ch_required_dict, logger):
    plot_list = [x, y]
    df = make_dataframe(dc_dict, plot_list, ch_required_dict, logger)
    return df.hvplot.scatter(x, y, s=20, c='b', height=400, width=400)
