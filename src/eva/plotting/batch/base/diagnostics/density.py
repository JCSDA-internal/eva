from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import numpy as np

from abc import ABC, abstractmethod

# --------------------------------------------------------------------------------------------------


class Density(ABC):

    """Base class for creating density plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a density plot abstract class based on the provided configuration and data.

        Args:
            config (dict): A dictionary containing the configuration for the density plot.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.

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

        self.config = config
        self.logger = logger
        self.dataobj = dataobj
        self.plotobj = None
        self.data = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self):

        """ Preparing data for configure_plot  """

        # Get the data to plot from the data_collection
        # ---------------------------------------------
        varstr = self.config['data']['variable']
        var_cgv = varstr.split('::')

        if len(var_cgv) != 3:
            self.logger.abort('In Density the variable \'var_cgv\' does not appear to ' +
                              'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in self.config['data']:
            channel = self.config['data'].get('channel')

        data = self.dataobj.get_variable_data(var_cgv[0], var_cgv[1], var_cgv[2], channel)

        # See if we need to slice data
        data = slice_var_from_str(self.config['data'], data, self.logger)

        # Density data should be flattened
        data = np.ravel(np.asanyarray(data))
        
        # If upstream gave us a masked array, turn masked to NaN for uniform handling
        if ma.isMaskedArray(data):
            data = data.filled(np.nan)
        
        # Optional knob: by default density plots *drop* NaNs (keeps current behavior)
        # Set `drop_nan: false` in the layer config if you want to preserve length (masked in place)
        drop_nan = bool(self.config.get('drop_nan', True))
        
        if drop_nan:
            # keep only finite values
            self.data = data[np.isfinite(data)]
        else:
            # preserve length, mask non-finite in place; downstream can decide whether to compress
            self.data = ma.masked_invalid(data)

# --------------------------------------------------------------------------------------------------

    @abstractmethod
    def configure_plot(self):
        """ Virtual method for configuring plot based on selected backend  """
        pass

# --------------------------------------------------------------------------------------------------
