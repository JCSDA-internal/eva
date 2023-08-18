from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import emcpy.plots.plots
import os
import numpy as np


# --------------------------------------------------------------------------------------------------


class Scatter():
    
    """Base class for creating scatter plots."""

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
            config = {
                "longitude": {"variable": "collection::group::variable"},
                "latitude": {"variable": "collection::group::variable"},
                "data": {"variable": "collection::group::variable", "channel": "channel_name"},
                "plot_property": "property_value",
                "plot_option": "option_value",
                "schema": "path_to_schema_file.yaml"
            }
            logger = Logger()
            map_scatter_plot = MapScatter(config, logger, None)
        """

        # Get the data to plot from the data_collection
        # ---------------------------------------------
        var0 = config['x']['variable']
        var1 = config['y']['variable']

        var0_cgv = var0.split('::')
        var1_cgv = var1.split('::')

        if len(var0_cgv) != 3:
            logger.abort('In Scatter comparison the first variable \'var0\' does not appear to ' +
                         'be in the required format of collection::group::variable.')
        if len(var1_cgv) != 3:
            logger.abort('In Scatter comparison the first variable \'var1\' does not appear to ' +
                         'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in config:
            channel = config.get('channel')

        xdata = dataobj.get_variable_data(var0_cgv[0], var0_cgv[1], var0_cgv[2], channel)
        xdata1 = dataobj.get_variable_data(var0_cgv[0], var0_cgv[1], var0_cgv[2])
        ydata = dataobj.get_variable_data(var1_cgv[0], var1_cgv[1], var1_cgv[2], channel)

        # see if we need to slice data
        xdata = slice_var_from_str(config['x'], xdata, logger)
        ydata = slice_var_from_str(config['y'], ydata, logger)

        # scatter data should be flattened
        xdata = xdata.flatten()
        ydata = ydata.flatten()

        # Remove NaN values to enable regression
        # --------------------------------------
        mask = ~np.isnan(xdata)
        xdata = xdata[mask]
        ydata = ydata[mask]

        mask = ~np.isnan(ydata)
        xdata = xdata[mask]
        ydata = ydata[mask]

        # Create declarative plotting Scatter object
        # ------------------------------------------
        self.plotobj = emcpy.plots.plots.Scatter(xdata, ydata)

        # Get defaults from schema
        # ------------------------
        layer_schema = config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'emcpy', 'defaults', 'scatter.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['x', 'y', 'type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)


# --------------------------------------------------------------------------------------------------
