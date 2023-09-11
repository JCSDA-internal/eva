# (C) Copyright 2023 NOAA/NWS/EMC
#
# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from eva.utilities.utils import replace_vars_dict, parse_channel_list
from bokeh.plotting import figure, output_file, save
import copy
import os

# --------------------------------------------------------------------------------------------------

def bokeh_figure_driver(config, data_collections, timing, logger):
    """
    Generates and saves multiple figures based on the provided configuration.

    Args:
        config (dict): A dictionary containing the configuration for generating figures.
        data_collections (DataCollections): An instance of the DataCollections class containing
        input data.
        timing (Timing): A timing instance to measure the execution time.
        logger (Logger): An instance of the logger for logging messages.

    This function generates and saves multiple figures based on the provided configuration. It
    processes each graphic specified in the configuration and creates corresponding figures with
    plots. This figure driver uses the bokeh backend to create interactive plots.
    """

    # Get list of graphics from configuration
    # -------------------
    graphics_section = config.get("graphics")
    graphics = graphics_section.get("figure_list")

    # Loop through specified graphics
    # -------------------
    timing.start('Graphics Loop')
    for graphic in graphics:

        # Parse configuration for this graphic
        # -------------------
        batch_conf = graphic.get("batch figure", {})  # batch configuration (default nothing)
        figure_conf = graphic.get("figure")  # figure configuration
        plot_conf = graphic.get("plot")
        #dynamic_options_conf = graphic.get("dynamic options", [])  # Dynamic overwrites

        # update figure conf based on schema - later
        # ----------------------------------

        # ---------------------------------------
        if batch_conf:
            # Get potential variables
            variables = batch_conf.get('variables', [])
            # Get list of channels
            channels_str_or_list = batch_conf.get('channels', [])
            channels = parse_channel_list(channels_str_or_list, logger)

            # Set some fake values to ensure the loops are entered
            if variables == []:
                logger.abort("Batch Figure must provide variables, even if with channels")
            if channels == []:
                channels = ['none']

            # Loop over variables and channels
            for variable in variables:
                for channel in channels:
                    batch_conf_this = {}
                    batch_conf_this['variable'] = variable
                    # Version to be used in titles
                    batch_conf_this['variable_title'] = variable.replace('_', ' ').title()
                    channel_str = str(channel)
                    if channel_str != 'none':
                        batch_conf_this['channel'] = channel_str
                        var_title = batch_conf_this['variable_title'] + ' Ch. ' + channel_str
                        batch_conf_this['variable_title'] = var_title

                    # Replace templated variables in figure and plots config
                    figure_conf_fill = copy.copy(figure_conf)
                    figure_conf_fill = replace_vars_dict(figure_conf_fill, **batch_conf_this)
                    plot_conf_fill = copy.copy(plot_conf)
                    plot_conf_fill = replace_vars_dict(plot_conf_fill, **batch_conf_this)
                    #dynamic_options_conf_fill = copy.copy(dynamic_options_conf)
                    #dynamic_options_conf_fill = replace_vars_dict(dynamic_options_conf_fill,
                    #                                              **batch_conf_this)

                    # Make plot
                    #make_figure(figure_conf_fill, plots_conf_fill,
                    #            dynamic_options_conf_fill, data_collections, logger)
                    make_figure(figure_conf_fill, plot_conf_fill, data_collections, logger)
        else:
            # make just one figure per configuration
            #make_figure(figure_conf, plots_conf, dynamic_options_conf, data_collections, logger)
            make_figure(figure_conf, plot_conf, data_collections, logger)
    timing.stop('Graphics Loop')

# --------------------------------------------------------------------------------------------------

def make_figure(figure_conf, plot, data_collections, logger):
    """
    Generates a figure based on the provided configuration and plots.

    Args:
        figure_conf (dict): A dictionary containing the configuration for the figure layout
                            and appearance.
        plots (list): A list of dictionaries containing plot configurations.
        data_collections (DataCollections): An instance of the DataCollections class containing
        input data.
        logger (Logger): An instance of the logger for logging messages.

    This function generates a figure based on the provided configuration and plot settings. It
    processes the specified plots, applies dynamic options, and saves the generated figure.
    """

    # set up figure
    fig = figure(title = figure_conf['title'],
           x_axis_label = plot['x_axis_label'],
           y_axis_label = plot['y_axis_label'])

    # retrieve variables from data collection
    x_args = plot['x']['variable'].split('::')
    y_args = plot['y']['variable'].split('::')
    x = data_collections.get_variable_data(x_args[0], x_args[1], x_args[2])
    y = data_collections.get_variable_data(y_args[0], y_args[1], y_args[2])
    fig.scatter(x, y)

    output_name = figure_conf['output name']
    dir_path = os.path.dirname(output_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    output_file(output_name)
    save(fig)
