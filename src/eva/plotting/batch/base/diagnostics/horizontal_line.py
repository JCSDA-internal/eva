from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from abc import ABC, abstractmethod
# --------------------------------------------------------------------------------------------------


class HorizontalLine():

    """Base class for creating horizontal line plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a horizontal line plot based on the provided configuration.

        Args:
            config (dict): A dictionary containing the configuration for the horizontal line plot.
            logger (Logger): An instance of the logger for logging messages.

        This class initializes and configures a horizontal line plot based on the provided
        configuration. The horizontal line plot is created using a declarative plotting library from
        EMCPy (https://github.com/NOAA-EMC/emcpy).

        Example:

            ::

                    config = {
                        "y": 0.5,
                        "plot_property": "property_value",
                        "plot_option": "option_value",
                        "schema": "path_to_schema_file.yaml"
                    }
                    logger = Logger()
                    horizontal_line_plot = HorizontalLine(config, logger)
        """

        self.config = config
        self.yval = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self):

        # Get the y value to plot
        # -----------------------
        self.yval = config['y']

# --------------------------------------------------------------------------------------------------

    @abstractmethod
    def configure_plot(self):
        pass



