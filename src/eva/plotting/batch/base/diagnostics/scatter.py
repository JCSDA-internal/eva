from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import numpy as np
import numpy.ma as ma

from abc import ABC, abstractmethod

# --------------------------------------------------------------------------------------------------


class Scatter(ABC):

    """Base class for creating scatter plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a scatter plot abstract class based on the provided configuration.

        Args:
            config (dict): A dictionary containing the configuration for the scatter plot on a map.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.


        Example:

            ::

                    config = {
                        "x": {"variable": "collection::group::variable"},
                        "y": {"variable": "collection::group::variable"},
                        "plot_property": "property_value",
                        "plot_option": "option_value",
                        "schema": "path_to_schema_file.yaml"
                    }
                    logger = Logger()
                    scatter_plot = Scatter(config, logger, None)
        """

        self.config = config
        self.logger = logger
        self.dataobj = dataobj
        self.xdata = []
        self.ydata = []
        self.plotobj = None

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
            self.logger.abort('Scatter: comparison first var \'var0\' does not appear to ' +
                              'be in the required format of collection::group::variable.')
        if len(var1_cgv) != 3:
            self.logger.abort('Scatter: comparison first var \'var1\' does not appear to ' +
                              'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in self.config:
            channel = self.config.get('channel')

        xdata = self.dataobj.get_variable_data(var0_cgv[0], var0_cgv[1], var0_cgv[2], channel)
        ydata = self.dataobj.get_variable_data(var1_cgv[0], var1_cgv[1], var1_cgv[2], channel)

        # Optional slicing
        xdata = slice_var_from_str(self.config['x'], xdata, self.logger)
        ydata = slice_var_from_str(self.config['y'], ydata, self.logger)

        # Flatten and normalize (turn masked to NaN for uniform handling)
        x = np.ravel(np.asanyarray(xdata))
        y = np.ravel(np.asanyarray(ydata))
        if ma.isMaskedArray(x):
            x = x.filled(np.nan)
        if ma.isMaskedArray(y):
            y = y.filled(np.nan)

        # Read & remove knob so it won't propagate to matplotlib kwargs
        cfg = dict(self.config)
        drop_nan = bool(cfg.pop('drop_nan', True))  # default True for scatter
        self.config = cfg

        if drop_nan:
            # Keep only pairs where both x and y are finite
            mask = np.isfinite(x) & np.isfinite(y)
            self.xdata = x[mask]
            self.ydata = y[mask]
        else:
            # Preserve length; mask invalid pairs in-place (some backends honor masked arrays)
            invalid = ~(np.isfinite(x) & np.isfinite(y))
            self.xdata = ma.array(x, mask=invalid)
            self.ydata = ma.array(y, mask=invalid)

    @abstractmethod
    def configure_plot(self):
        """ Virtual method for configuring plot based on selected backend  """
        pass

# --------------------------------------------------------------------------------------------------
