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
        timing (Timing): A timing instance to measure the execution time.
        logger (Logger): An instance of the logger for logging messages.

    This function generates and saves multiple figures based on the provided configuration. It
    processes each graphic specified in the configuration and creates corresponding figures with
    plots. This function also uses the plotting backend specified in the configuration.
    """

    # Get list of graphics from configuration
    # -------------------
    graphics_section = config.get('graphics')
    graphics = graphics_section.get('figure_list')

    # Get plotting backend
    # --------------------
    backend = graphics_section.get('plotting_backend')

    if backend not in ['Emcpy', 'Hvplot']:
        logger.abort('Backend not found. \
                     Available backends: Emcpy, Hvplot')

    if backend == 'Hvplot':
        try:
            import hvplot
        except ImportError:
            logger.abort("The hvplot backend is not available since \
                         hvplot is not in the environment.")

    # Create handler
    # --------------
    handler_class_name = backend + 'FigureHandler'
    handler_module_name = camelcase_to_underscore(handler_class_name)
    handler_full_module = 'eva.plotting.batch.' + \
                          backend.lower() + '.plot_tools.' + handler_module_name
    handler_class = getattr(im.import_module(handler_full_module), handler_class_name)
    handler = handler_class()

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
        fig_schema = figure_conf.get('schema', os.path.join(return_eva_path(), 'plotting', 'batch',
                                     backend.lower(), 'defaults', 'figure.yaml'))
        figure_conf = get_schema(fig_schema, figure_conf, logger)

        # pass configurations and make graphic(s)
        # ---------------------------------------
        if batch_conf:
            # Get potential variables
            variables = batch_conf.get('variables', [])

            # Get list of channels and load step variables
            channels_str_or_list = batch_conf.get('channels', [])
            channels = parse_channel_list(channels_str_or_list, logger)

            step_vars = channels if channels else ['none']
            step_var_name = 'channel'
            title_fill = ' Ch. '

            # Get list of levels, load step variables
            levels_str_or_list = batch_conf.get('levels', [])
            levels = parse_channel_list(levels_str_or_list, logger)
            if levels:
                step_vars = levels
                step_var_name = 'level'
                title_fill = ' Lev. '

            # Get list of datatypes and load step variables
            datatypes = batch_conf.get('datatypes', [])
            if datatypes:
                step_vars = datatypes
                step_var_name = 'datatype'
                title_fill = ' Dtype. '

            # Set some fake values to ensure the loops are entered
            if not variables:
                logger.abort("Batch Figure must provide variables, even if with channels")

            # Loop over variables and channels
            # FUTURE NOTE: This can be parallelized. Could add multiprocessing option.
            for variable in variables:
                for step_var in step_vars:
                    batch_conf_this = {}
                    batch_conf_this['variable'] = variable

                    # Version to be used in titles
                    batch_conf_this['variable_title'] = variable.replace('_', ' ').title()

                    step_var_str = str(step_var)
                    if step_var_str != 'none':
                        batch_conf_this[step_var_name] = step_var_str
                        var_title = batch_conf_this['variable_title'] + title_fill + step_var_str
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
                    make_figure(handler, figure_conf_fill, plots_conf_fill,
                                dynamic_options_conf_fill, data_collections, logger)

        else:
            # make just one figure per configuration
            make_figure(handler, figure_conf, plots_conf,
                        dynamic_options_conf, data_collections, logger)
    timing.stop('Graphics Loop')


# --------------------------------------------------------------------------------------------------


def make_figure(handler, figure_conf, plots, dynamic_options, data_collections, logger):
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
        mod_name = "eva.plotting.batch.base.plot_tools.dynamic_config"
        dynamic_option_module = im.import_module(mod_name)
        dynamic_option_method = getattr(dynamic_option_module, dynamic_option['type'])
        plots = dynamic_option_method(logger, dynamic_option, plots, data_collections)

    # Setup figure details
    # --------------------
    nrows, ncols = figure_conf.get("layout", (1, 1))
    figsize = tuple(figure_conf.get("figure size", (10, 8)))
    output_file = get_output_file(figure_conf)
    file_type = figure_conf.get("figure file type", "png")

    # Initialize layer cache
    layer_class_cache = {}

    def get_layer_class(layer_type):
        eva_class_name = handler.BACKEND_NAME + layer_type
        if eva_class_name not in layer_class_cache:
            module_name = camelcase_to_underscore(eva_class_name)
            full_module = handler.MODULE_NAME + module_name
            layer_class_cache[eva_class_name] = getattr(
                im.import_module(full_module), eva_class_name
            )
        return layer_class_cache[eva_class_name]

    # Build all subplots
    plot_list = []
    # FUTURE NOTE: This can be parallelized. Could add multiprocessing option.
    for plot in plots:
        # 1. Configure each layer
        layer_list = []
        for layer_cfg in plot.get("layers", []):
            layer_type = layer_cfg.get("type")
            if not layer_type:
                logger.warning("Layer missing 'type': %s", layer_cfg)
                continue
            layer_class = get_layer_class(layer_type)
            layer_obj = layer_class(layer_cfg, logger, data_collections)
            layer_obj.data_prep()
            layer_list.append(layer_obj.configure_plot())

        # 2. Extract mapping (projection/domain)
        proj, domain = None, None
        if "mapping" in plot:
            mapopt = plot["mapping"]
            proj = mapopt.get("projection")
            domain = mapopt.get("domain")

        # 3. Create plot object
        plotobj = handler.create_plot(layer_list, proj, domain)

        # 4. Apply additional plot configuration
        for key, value in plot.items():
            if key in ["layers", "mapping"]:
                continue  # already processed
            if key == "statistics":
                stats_helper(logger, plotobj, data_collections, value)
                continue

            # Refactored to call `getattr()` once and
            # add fail safe if method does not exist
            method = getattr(plotobj, key, None)
            if callable(method):
                try:
                    if isinstance(value, dict):
                        method(**value)
                    elif value is None:
                        method()
                    else:
                        method(value)
                except Exception as e:
                    logger.warning(f"Failed to apply plot method '{key}': {e}")
            else:
                logger.warning(f"Unknown plot method: '{key}'")

        plot_list.append(plotobj)

    # Create figure and attach subplots
    fig = handler.create_figure(nrows, ncols, figsize)
    fig.plot_list = plot_list
    fig.create_figure()

    if "title" in figure_conf:
        fig.add_suptitle(figure_conf['title'])
    if "tight layout" in figure_conf:
        layout_val = figure_conf.pop("tight layout")
        fig.tight_layout(**layout_val) if isinstance(layout_val, dict) else fig.tight_layout()
    if "plot logo" in figure_conf:
        fig.plot_logo(**figure_conf.pop("plot logo"))

    # Save and close
    fig.save_figure(output_file, **get_saveargs(figure_conf))
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
