from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import numpy as np

from abc import ABC, abstractmethod

# --------------------------------------------------------------------------------------------------


class LinePlot(ABC):

    """Base class for creating line plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a line plot abstract class based on the provided configuration.

        Args:
            config (dict): A dictionary containing the configuration for the line plot.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.


        Example:

            ::

                    config = {
                        "x": {"variable": "collection::group::variable"},
                        "y": {"variable": "collection::group::variable"},
                        "channel": "channel_name",
                        "plot_property": "property_value",
                        "plot_option": "option_value",
                        "schema": "path_to_schema_file.yaml"
                    }
                    logger = Logger()
                    line_plot = LinePlot(config, logger, None)
        """

        self.dataobj = dataobj
        self.config = config
        self.logger = logger
        self.xdata = None
        self.ydata = None
        self.plotobj = None

        self.color = None
        self.label = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self):
        """ Preparing data for configure_plot  """

        # Get the data to plot from the data_collection
        # ---------------------------------------------
        var0 = self.config['x']['variable']
        var1 = self.config['y']['variable']

        var0_cgv = var0.split('::')
        var1_cgv = var1.split('::')

        if len(var0_cgv) != 3:
            self.logger.abort('In Scatter comparison the first variable \'var0\' ' +
                              'does not appear to be in the required format of ' +
                              'collection::group::variable.')
        if len(var1_cgv) != 3:
            self.logger.abort('In Scatter comparison the first variable \'var1\' ' +
                              'does not appear to be in the required format of ' +
                              'collection::group::variable.')

        # Optionally get the channel|level|datatype to plot
        channel = None
        if 'channel' in self.config:
            channel = self.config.get('channel')
        level = None
        if 'level' in self.config:
            level = self.config.get('level')
        datatype = None
        if 'datatype' in self.config:
            datatype = self.config.get('datatype')
        if 'color' in self.config:
            self.color = self.config.get('color')
        if 'label' in self.config:
            self.label = self.config.get('label')

        xdata = self.dataobj.get_variable_data(var0_cgv[0], var0_cgv[1], var0_cgv[2],
                                               channel, level, datatype)
        ydata = self.dataobj.get_variable_data(var1_cgv[0], var1_cgv[1], var1_cgv[2],
                                               channel, level, datatype)

        # see if we need to slice data
        xdata = slice_var_from_str(self.config['x'], xdata, self.logger)
        ydata = slice_var_from_str(self.config['y'], ydata, self.logger)

        # line plot data should be flattened
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

# --------------------------------------------------------------------------------------------------

    @abstractmethod
    def configure_plot(self):
        """ Virtual method for configuring plot based on selected backend  """
        pass
