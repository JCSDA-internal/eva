from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
#import emcpy.plots.plots
import os
import numpy as np

from abc import ABC, abstractmethod

# --------------------------------------------------------------------------------------------------


class Scatter(ABC):

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
        self.config = config
        self.logger = logger
        self.dataobj = dataobj
        self.xdata = []
        self.ydata = []
        self.plotobj = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self): 

        # Get the data to plot from the data_collection
        # ---------------------------------------------
        var0 = self.config['x']['variable']
        var1 = self.config['y']['variable']

        var0_cgv = var0.split('::')
        var1_cgv = var1.split('::')

        if len(var0_cgv) != 3:
            self.logger.abort('In Scatter comparison the first variable \'var0\' does not appear to ' +
                         'be in the required format of collection::group::variable.')
        if len(var1_cgv) != 3:
            self.logger.abort('In Scatter comparison the first variable \'var1\' does not appear to ' +
                         'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in self.config:
            channel = self.config.get('channel')

        xdata = self.dataobj.get_variable_data(var0_cgv[0], var0_cgv[1], var0_cgv[2], channel)
        xdata1 = self.dataobj.get_variable_data(var0_cgv[0], var0_cgv[1], var0_cgv[2])
        ydata = self.dataobj.get_variable_data(var1_cgv[0], var1_cgv[1], var1_cgv[2], channel)

        # see if we need to slice data
        xdata = slice_var_from_str(self.config['x'], xdata, self.logger)
        ydata = slice_var_from_str(self.config['y'], ydata, self.logger)

        # scatter data should be flattened
        xdata = xdata.flatten()
        ydata = ydata.flatten()

        # Remove NaN values to enable regression
        # --------------------------------------
        mask = ~np.isnan(xdata)
        xdata = xdata[mask]
        ydata = ydata[mask]

        mask = ~np.isnan(ydata)
        self.xdata = xdata[mask]
        self.ydata = ydata[mask]


    @abstractmethod
    def configure_plot(self):
        pass

# --------------------------------------------------------------------------------------------------
