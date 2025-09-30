from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import numpy as np
import numpy.ma as ma

from abc import ABC, abstractmethod

# --------------------------------------------------------------------------------------------------


class Histogram(ABC):

    """Base class for creating histogram plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a histogram plot abstract class based on the provided configuration and data.

        Args:
            config (dict): A dictionary containing the configuration for the histogram plot.
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
                    histogram_plot = Histogram(config, logger, dataobj)
        """

        self.config = config
        self.logger = logger
        self.dataobj = dataobj
        self.data = None
        self.plotobj = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self):
        """ Preparing data for configure_plot  """

        # Get the data to plot from the data_collection
        # ---------------------------------------------
        varstr = self.config['data']['variable']
        var_cgv = varstr.split('::')

        if len(var_cgv) != 3:
            logger.abort('In Histogram the variable \'var_cgv\' does not appear to ' +
                         'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in self.config['data']:
            channel = self.config['data'].get('channel')

        data = self.dataobj.get_variable_data(var_cgv[0], var_cgv[1], var_cgv[2], channel)

        # See if we need to slice data
        data = slice_var_from_str(self.config['data'], data, self.logger)

        # Flatten
        arr = np.ravel(np.asanyarray(data))

        # If masked, convert masked entries to NaN for uniform handling
        if ma.isMaskedArray(arr):
            arr = arr.filled(np.nan)

        # Read & strip the knob so it never leaks to backends
        cfg = dict(self.config)
        drop_nan = bool(cfg.get('drop_nan', True))
        cfg.pop('drop_nan', None)
        self.config = cfg

        if drop_nan:
            # Typical histogram path: use only finite values
            self.data = arr[np.isfinite(arr)]
        else:
            # Preserve length and mask invalids in place (backend must accept masked arrays)
            self.data = ma.masked_invalid(arr)

# --------------------------------------------------------------------------------------------------

    @abstractmethod
    def configure_plot(self):
        """ Virtual method for configuring plot based on selected backend  """
        pass

# --------------------------------------------------------------------------------------------------
