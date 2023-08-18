from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os


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
            config = {
                "y": 0.5,
                "plot_property": "property_value",
                "plot_option": "option_value",
                "schema": "path_to_schema_file.yaml"
            }
            logger = Logger()
            horizontal_line_plot = HorizontalLine(config, logger)
        """

        # Get the y value to plot
        # -----------------------
        yval = config['y']

        # Create declarative plotting HorizontalLine object
        # -------------------------------------------
        self.plotobj = emcpy.plots.plots.HorizontalLine(yval)

        # Get defaults from schema
        # ------------------------
        layer_schema = config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'emcpy', 'defaults',
                                                         'horizontal_line.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)


# --------------------------------------------------------------------------------------------------
