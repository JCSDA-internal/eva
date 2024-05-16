from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import numpy as np

from abc import ABC, abstractmethod

# --------------------------------------------------------------------------------------------------


class MapScatter(ABC):

    """Base class for creating map scatter plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a scatter plot on a map based on the provided configuration.

        Args:
            config (dict): A dictionary containing the configuration for the scatter plot on a map.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.


        Example:
            ::

                    config = {
                        "longitude": {"variable": "collection::group::variable"},
                        "latitude": {"variable": "collection::group::variable"},
                        "data": {"variable": "collection::group::variable",
                                 "channel": "channel_name"},
                        "plot_property": "property_value",
                        "plot_option": "option_value",
                        "schema": "path_to_schema_file.yaml"
                    }
                    logger = Logger()
                    map_scatter_plot = MapScatter(config, logger, None)
        """

        self.config = config
        self.logger = logger
        self.dataobj = dataobj
        self.lonvar = None
        self.latvar = None
        self.datavar = None
        self.plotobj = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self):
        """ Preparing data for configure_plot  """

        channel = None
        if 'channel' in self.config['data']:
            channel = self.config['data'].get('channel')
        lonvar_cgv = self.config['longitude']['variable'].split('::')
        lonvar = self.dataobj.get_variable_data(lonvar_cgv[0], lonvar_cgv[1], lonvar_cgv[2], None)
        lonvar = slice_var_from_str(self.config['longitude'], lonvar, self.logger)
        latvar_cgv = self.config['latitude']['variable'].split('::')
        latvar = self.dataobj.get_variable_data(latvar_cgv[0], latvar_cgv[1], latvar_cgv[2], None)
        latvar = slice_var_from_str(self.config['latitude'], latvar, self.logger)
        datavar_cgv = self.config['data']['variable'].split('::')
        datavar = self.dataobj.get_variable_data(datavar_cgv[0], datavar_cgv[1],
                                                 datavar_cgv[2], channel)
        datavar = slice_var_from_str(self.config['data'], datavar, self.logger)
        self.lonvar = lonvar.flatten()
        self.latvar = latvar.flatten()
        self.datavar = datavar.flatten()

        # If everything is nan plotting will fail so just plot some large values
        if np.isnan(self.datavar).all():
            self.datavar[np.isnan(self.datavar)] = 1.0e38

# --------------------------------------------------------------------------------------------------

    @abstractmethod
    def configure_plot(self):
        """ Virtual method for configuring plot based on selected backend  """

        pass

# --------------------------------------------------------------------------------------------------
