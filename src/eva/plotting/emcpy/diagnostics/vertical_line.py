from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os


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

        # Get the x value to plot
        # -----------------------
        xval = config['x']

        # Create declarative plotting HorizontalLine object
        # -------------------------------------------
        self.plotobj = emcpy.plots.plots.VerticalLine(xval)

        # Get defaults from schema
        # ------------------------
        layer_schema = config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'emcpy', 'defaults', 'vertical_line.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)


# --------------------------------------------------------------------------------------------------
