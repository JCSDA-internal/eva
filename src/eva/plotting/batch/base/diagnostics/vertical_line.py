from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from abc import ABC, abstractmethod
# --------------------------------------------------------------------------------------------------


class VerticalLine():

    """Base class for creating vertical line plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a vertical line plot based on the provided configuration.

        Args:
            config (dict): A dictionary containing the configuration for the vertical line plot.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: Not used in this context.

        This class initializes and configures a vertical line plot based on the provided
        configuration. The vertical line plot is created using a declarative plotting library from
        EMCPy (https://github.com/NOAA-EMC/emcpy).

        Example:

            ::

                    config = {
                        "x": 10,
                        "plot_property": "property_value",
                        "plot_option": "option_value",
                        "schema": "path_to_schema_file.yaml"
                    }
                    logger = Logger()
                    vertical_line_plot = VerticalLine(config, logger, None)
        """

        self.logger = logger
        self.config = config
        self.xval = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self):

        # Get the x value to plot
        # -----------------------
        self.xval = self.config['x']
        

# --------------------------------------------------------------------------------------------------

    @abstractmethod
    def configure_plot(self):
        pass

                
