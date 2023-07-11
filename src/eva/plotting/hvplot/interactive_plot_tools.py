import pandas as pd
import hvplot.pandas
import geopandas as gpd

def hvplot_line_plot(dc_dict, plot_list, ch_required_dict, logger):
    df = pd.DataFrame()
    for item in plot_list:
        item_list = item.split('::')
        if len(item_list) == 3:
            collection = item_list[0]
            group = item_list[1]
            variable = item_list[2]

            if ch_required_dict[collection] == True:
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
    return df.hvplot.line()

# --------------------------------------------------------------------------------------------------

def hvplot_histogram(dc_dict, plot_list, ch_required_dict, logger):
    #Make empty dataframe
    df = pd.DataFrame()
    for item in plot_list:
        item_list = item.split('::')
        if len(item_list) == 3:
            collection = item_list[0]
            group = item_list[1]
            variable = item_list[2]

            if ch_required_dict[collection] == True:
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
    return df.hvplot.hist(bins=100)

# --------------------------------------------------------------------------------------------------

def hvplot_map_scatter(dc_dict, plot_entry):
    #retrieve latitude, longitude, and variable
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

def hvplot_density_plot(plot_list, ch_required_dict, logger):

    #Make empty dataframe
    df = pd.DataFrame()
    for item in plot_list:
        item_list = item.split('::')
        if len(item_list) == 3:
            collection = item_list[0]
            group = item_list[1]
            variable = item_list[2]

            if ch_required_dict[collection] == True:
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
        #print(np.count_nonzero(~np.isnan(arr)))

    #if print_stats:
    #    print_statistics(df)
    df = df.dropna()

    return df.hvplot.kde(filled=True, legend='top_left', alpha=0.5, bandwidth=0.1, height=400)

# --------------------------------------------------------------------------------------------------

def hvplot_scatter(dc_dict, x, y, ch_required_dict, logger):
    df = pd.DataFrame()
    plot_list = [x, y]
    for item in plot_list:
        #split would break here if no channel and channel required, use try/except
        #block and no need to check for channel required
        item_list = item.split('::')
        #print(item_list)
        #print(len(item_list))
        if len(item_list) == 3:
            collection = item_list[0]
            group = item_list[1]
            variable = item_list[2]

            if ch_required_dict[collection] == True:
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
    #if print_stats:
    #    print_statistics(df)

    return df.hvplot.scatter(x, y, s=20, c='b', height=400, width=400)
