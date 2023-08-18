from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import emcpy.plots.map_plots
import os
import numpy as np


# --------------------------------------------------------------------------------------------------


class MapScatter():

    """Base class for creating map scatter plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a scatter plot on a map based on the provided configuration.

        Args:
            config (dict): A dictionary containing the configuration for the scatter plot on a map.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.

        This class initializes and configures a scatter plot on a map based on the provided
        configuration. The scatter plot is created using a declarative plotting library from EMCPy
        (https://github.com/NOAA-EMC/emcpy).

        Example:
            ::

                    config = {
                        "longitude": {"variable": "collection::group::variable"},
                        "latitude": {"variable": "collection::group::variable"},
                        "data": {"variable": "collection::group::variable",
                                 "channel": "channel_name"},
                        "plot_property": "property_value",
                        "plot_option": "option_value",
                        "schema": "path_to_schema_file.yaml"
                    }
                    logger = Logger()
                    map_scatter_plot = MapScatter(config, logger, None)
        """

        # prepare data based on config
        # Optionally get the channel to plot
        channel = None
        if 'channel' in config['data']:
            channel = config['data'].get('channel')
        lonvar_cgv = config['longitude']['variable'].split('::')
        lonvar = dataobj.get_variable_data(lonvar_cgv[0], lonvar_cgv[1], lonvar_cgv[2], None)
        lonvar = slice_var_from_str(config['longitude'], lonvar, logger)
        latvar_cgv = config['latitude']['variable'].split('::')
        latvar = dataobj.get_variable_data(latvar_cgv[0], latvar_cgv[1], latvar_cgv[2], None)
        latvar = slice_var_from_str(config['latitude'], latvar, logger)
        datavar_cgv = config['data']['variable'].split('::')
        datavar = dataobj.get_variable_data(datavar_cgv[0], datavar_cgv[1], datavar_cgv[2], channel)
        datavar = slice_var_from_str(config['data'], datavar, logger)
        # scatter data should be flattened
        lonvar = lonvar.flatten()
        latvar = latvar.flatten()
        datavar = datavar.flatten()

        # If everything is nan plotting will fail so just plot some large values
        if np.isnan(datavar).all():
            datavar[np.isnan(datavar)] = 1.0e38

        # create declarative plotting MapScatter object
        self.plotobj = emcpy.plots.map_plots.MapScatter(latvar, lonvar, datavar)
        # get defaults from schema
        layer_schema = config.get("schema",
                                  os.path.join(return_eva_path(),
                                               'plotting',
                                               'emcpy', 'defaults',
                                               'map_scatter.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['longitude', 'latitude', 'data', 'type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)


# --------------------------------------------------------------------------------------------------
