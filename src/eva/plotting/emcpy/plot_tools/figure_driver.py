# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from eva.eva_path import return_eva_path
from eva.utilities.stats import stats_helper
from eva.utilities.utils import get_schema, camelcase_to_underscore, parse_channel_list
from eva.utilities.utils import replace_vars_dict
from emcpy.plots.create_plots import CreatePlot, CreateFigure
import copy
import importlib as im
import os

# --------------------------------------------------------------------------------------------------


def figure_driver(config, data_collections, timing, logger):
    """
    Generates and saves multiple figures based on the provided configuration.

    Args:
        config (dict): A dictionary containing the configuration for generating figures.
        data_collections (DataCollections): An instance of the DataCollections class containing
        input data.
        timing: A timing instance to measure the execution time.
        logger (Logger): An instance of the logger for logging messages.

    This function generates and saves multiple figures based on the provided configuration. It
    processes each graphic specified in the configuration and creates corresponding figures with
    plots.
    """

    # Get list of graphics from configuration
    # -------------------
    graphics = config.get("graphics")

    # Loop through specified graphics
    # -------------------
    timing.start('Graphics Loop')
    for graphic in graphics:

        # Parse configuration for this graphic
        # -------------------
        batch_conf = graphic.get("batch figure", {})  # batch configuration (default nothing)
        figure_conf = graphic.get("figure")  # figure configuration
        plots_conf = graphic.get("plots")  # list of plots/subplots
        dynamic_options_conf = graphic.get("dynamic options", [])  # Dynamic overwrites

        # update figure conf based on schema
        # ----------------------------------
        fig_schema = figure_conf.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                            'emcpy', 'defaults', 'figure.yaml'))
        figure_conf = get_schema(fig_schema, figure_conf, logger)

        # pass configurations and make graphic(s)
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
                    plots_conf_fill = copy.copy(plots_conf)
                    plots_conf_fill = replace_vars_dict(plots_conf_fill, **batch_conf_this)
                    dynamic_options_conf_fill = copy.copy(dynamic_options_conf)
                    dynamic_options_conf_fill = replace_vars_dict(dynamic_options_conf_fill,
                                                                  **batch_conf_this)

                    # Make plot
                    make_figure(figure_conf_fill, plots_conf_fill,
                                dynamic_options_conf_fill, data_collections, logger)
        else:
            # make just one figure per configuration
            make_figure(figure_conf, plots_conf, dynamic_options_conf, data_collections, logger)
    timing.stop('Graphics Loop')


# --------------------------------------------------------------------------------------------------


def make_figure(figure_conf, plots, dynamic_options, data_collections, logger):
    """
    Generates a figure based on the provided configuration and plots.

    Args:
        figure_conf (dict): A dictionary containing the configuration for the figure layout
                            and appearance.
        plots (list): A list of dictionaries containing plot configurations.
        dynamic_options (list): A list of dictionaries containing dynamic configuration options.
        data_collections (DataCollections): An instance of the DataCollections class containing
        input data.
        logger (Logger): An instance of the logger for logging messages.

    This function generates a figure based on the provided configuration and plot settings. It
    processes the specified plots, applies dynamic options, and saves the generated figure.
    """

    # Adjust the plots configs if there are dynamic options
    # -----------------------------------------------------
    for dynamic_option in dynamic_options:
        dynamic_option_module = im.import_module("eva.plotting.emcpy.plot_tools.dynamic_config")
        dynamic_option_method = getattr(dynamic_option_module, dynamic_option['type'])
        plots = dynamic_option_method(logger, dynamic_option, plots, data_collections)

    # Grab some figure configuration
    # -------------------
    figure_layout = figure_conf.get("layout")
    file_type = figure_conf.get("figure file type", "png")
    output_file = get_output_file(figure_conf)

    # Set up layers and plots
    plot_list = []
    for plot in plots:
        layer_list = []
        for layer in plot.get("layers"):
            eva_class_name = layer.get("type")
            eva_module_name = camelcase_to_underscore(eva_class_name)
            full_module = "eva.plotting.emcpy.diagnostics."+eva_module_name
            layer_class = getattr(im.import_module(full_module), eva_class_name)
            # use the translator class to go from eva to declarative plotting
            layer_list.append(layer_class(layer, logger, data_collections).plotobj)
        # get mapping dictionary
        proj = None
        domain = None
        if 'mapping' in plot.keys():
            mapoptions = plot.get('mapping')
            # TODO make this configurable and not hard coded
            proj = mapoptions['projection']
            domain = mapoptions['domain']

        # create a subplot based on specified layers
        plotobj = CreatePlot(plot_layers=layer_list, projection=proj, domain=domain)
        # make changes to subplot based on YAML configuration
        for key, value in plot.items():
            if key not in ['layers', 'mapping', 'statistics']:
                if isinstance(value, dict):
                    getattr(plotobj, key)(**value)
                elif value is None:
                    getattr(plotobj, key)()
                else:
                    getattr(plotobj, key)(value)
            if key in ['statistics']:
                # call the stats helper
                stats_helper(logger, plotobj, data_collections, value)

        plot_list.append(plotobj)
    # create figure
    fig = CreateFigure(nrows=figure_conf['layout'][0],
                       ncols=figure_conf['layout'][1],
                       figsize=tuple(figure_conf['figure size']))
    fig.plot_list = plot_list
    fig.create_figure()

    if 'title' in figure_conf:
        fig.add_suptitle(figure_conf['title'])
    if 'tight layout' in figure_conf:
        if isinstance(figure_conf['tight layout'], dict):
            fig.tight_layout(**figure_conf['tight layout'])
        else:
            fig.tight_layout()
    if 'plot logo' in figure_conf:
        fig.plot_logo(**figure_conf['plot logo'])

    saveargs = get_saveargs(figure_conf)
    fig.save_figure(output_file, **saveargs)

    fig.close_figure()


# --------------------------------------------------------------------------------------------------


def get_saveargs(figure_conf):
    """
    Gets arguments for saving a figure based on the provided configuration.

    Args:
        figure_conf (dict): A dictionary containing the figure configuration.

    Returns:
        out_conf (dict): A dictionary containing arguments for saving the figure.

    This function extracts relevant arguments from the provided figure configuration to be used
    for saving the generated figure.

    Example:
        ::

                figure_conf = {
                    "layout": [2, 2],
                    "figure file type": "png",
                    "output path": "./output_folder",
                    "output name": "example_figure"
                }
                save_args = get_saveargs(figure_conf)
    """

    out_conf = figure_conf
    delvars = ['layout', 'figure file type', 'output path', 'figure size', 'title']
    out_conf['format'] = figure_conf['figure file type']
    for d in delvars:
        del out_conf[d]
    return out_conf


# --------------------------------------------------------------------------------------------------


def get_output_file(figure_conf):
    """
    Gets the output file path for saving the figure.

    Args:
        figure_conf (dict): A dictionary containing the figure configuration.

    Returns:
        output_file (str): The complete path for saving the figure.

    This function constructs the complete file path for saving the generated figure based on the
    provided figure configuration.

    Example:
        ::

            figure_conf = {
                "output path": "./output_folder",
                "output name": "example_figure"
            }
            output_file = get_output_file(figure_conf)
    """

    file_path = figure_conf.get("output path", "./")
    output_name = figure_conf.get("output name", "")
    output_file = os.path.join(file_path, output_name)
    return output_file


# --------------------------------------------------------------------------------------------------
