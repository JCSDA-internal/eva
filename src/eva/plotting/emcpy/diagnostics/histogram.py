from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import emcpy.plots.plots
import os
import numpy as np


# --------------------------------------------------------------------------------------------------


class Histogram():

    """Base class for creating histogram plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a histogram plot based on the provided configuration and data.

        Args:
            config (dict): A dictionary containing the configuration for the histogram plot.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.

        This class initializes and configures a histogram plot based on the provided configuration and
        data. The histogram plot is created using a declarative plotting library from EMCPy
        (https://github.com/NOAA-EMC/emcpy).

        Example:
            config = {
                "data": {
                    "variable": "collection::group::variable",
                    "channel": "channel_name",
                    "slicing": "slice expression"
                },
                "plot_property": "property_value",
                "plot_option": "option_value",
                "schema": "path_to_schema_file.yaml"
            }
            logger = Logger()
            dataobj = DataObject()
            histogram_plot = Histogram(config, logger, dataobj)
        """

        # Get the data to plot from the data_collection
        # ---------------------------------------------
        varstr = config['data']['variable']
        var_cgv = varstr.split('::')

        if len(var_cgv) != 3:
            logger.abort('In Histogram the variable \'var_cgv\' does not appear to ' +
                         'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in config['data']:
            channel = config['data'].get('channel')

        data = dataobj.get_variable_data(var_cgv[0], var_cgv[1], var_cgv[2], channel)

        # See if we need to slice data
        data = slice_var_from_str(config['data'], data, logger)

        # Histogram data should be flattened
        data = data.flatten()

        # Missing data should also be removed
        mask = ~np.isnan(data)
        data = data[mask]

        # Create declarative plotting histogram object
        # --------------------------------------------
        self.plotobj = emcpy.plots.plots.Histogram(data)

        # Get defaults from schema
        # ------------------------
        layer_schema = config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'emcpy', 'defaults', 'histogram.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['type', 'schema', 'data']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)


# --------------------------------------------------------------------------------------------------
