from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import emcpy.plots.plots
import os
import numpy as np


# --------------------------------------------------------------------------------------------------


class Density():

    """Base class for creating density plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a density plot based on the provided configuration and data.

        Args:
            config (dict): A dictionary containing the configuration for the density plot.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.

        This class initializes and configures a density plot based on the provided configuration and
        data. The density plot is created using a declarative plotting library from EMCPy
        (https://github.com/NOAA-EMC/emcpy).

        Example:

            ::

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
                    density_plot = Density(config, logger, dataobj)
        """

        # Get the data to plot from the data_collection
        # ---------------------------------------------
        varstr = config['data']['variable']
        var_cgv = varstr.split('::')

        if len(var_cgv) != 3:
            logger.abort('In Density the variable \'var_cgv\' does not appear to ' +
                         'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in config['data']:
            channel = config['data'].get('channel')

        data = dataobj.get_variable_data(var_cgv[0], var_cgv[1], var_cgv[2], channel)

        # See if we need to slice data
        data = slice_var_from_str(config['data'], data, logger)

        # Density data should be flattened
        data = data.flatten()

        # Missing data should also be removed
        mask = ~np.isnan(data)
        data = data[mask]

        # Create declarative plotting density object
        # --------------------------------------------
        self.plotobj = emcpy.plots.plots.Density(data)

        # Get defaults from schema
        # ------------------------
        layer_schema = config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'emcpy', 'defaults', 'density.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['type', 'schema', 'data']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)


# --------------------------------------------------------------------------------------------------
