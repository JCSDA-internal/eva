from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import numpy as np

from abc import ABC, abstractmethod

# --------------------------------------------------------------------------------------------------


class ContourPlot(ABC):

    """Base class for creating Contour plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a Contour plot abstract class based on the provided configuration.

        Args:
            config (dict): A dictionary containing the configuration for the contour plot on a map.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.


        Example:

            ::

                    config = {
                        "x": {"variable": "collection::group::variable"},
                        "y": {"variable": "collection::group::variable"},
                        "z": {"variable": "collection::group::variable"},
                        "plot_property": "property_value",
                        "plot_option": "option_value",
                        "schema": "path_to_schema_file.yaml"
                    }
                    logger = Logger()
                    contour_plot = ContourPlot(config, logger, None)
        """

        self.config = config
        self.logger = logger
        self.dataobj = dataobj
        self.xdata = []
        self.ydata = []
        self.zdata = []
        self.plotobj = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self):
        """ Preparing data for configure_plot  """

        # Get the data to plot from the data_collection
        # ---------------------------------------------
        var0 = self.config['x']['variable']
        var1 = self.config['y']['variable']
        var2 = self.config['z']['variable']

        var0_cgv = var0.split('::')
        var1_cgv = var1.split('::')
        var2_cgv = var2.split('::')

        if len(var0_cgv) != 3:
            self.logger.abort('Contour: comparison first var \'var0\' does not appear to ' +
                              'be in the required format of collection::group::variable.')
        if len(var1_cgv) != 3:
            self.logger.abort('Contour: comparison second var \'var1\' does not appear to ' +
                              'be in the required format of collection::group::variable.')
        if len(var2_cgv) != 3:
            self.logger.abort('Contour: comparison second var \'var2\' does not appear to ' +
                              'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in self.config:
            channel = self.config.get('channel')

        xdata = self.dataobj.get_variable_data(var0_cgv[0], var0_cgv[1], var0_cgv[2], channel)
        ydata = self.dataobj.get_variable_data(var1_cgv[0], var1_cgv[1], var1_cgv[2], channel)
        zdata = self.dataobj.get_variable_data(var2_cgv[0], var2_cgv[1], var2_cgv[2], channel)

        # see if we need to slice data
        xdata = slice_var_from_str(self.config['x'], xdata, self.logger)
        ydata = slice_var_from_str(self.config['y'], ydata, self.logger)
        zdata = slice_var_from_str(self.config['z'], zdata, self.logger)

        # contour data should be flattened
        xdata = xdata.flatten()
        ydata = ydata.flatten()
        zdata = zdata.flatten()

    @abstractmethod
    def configure_plot(self):
        """ Virtual method for configuring plot based on selected backend  """
        pass

# --------------------------------------------------------------------------------------------------
