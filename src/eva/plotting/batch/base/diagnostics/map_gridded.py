from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import os

import numpy as np
from abc import ABC, abstractmethod

# --------------------------------------------------------------------------------------------------


class MapGridded(ABC):

    """Base class for creating map gridded plots."""

    def __init__(self, config, logger, dataobj):

        """
        Creates a gridded map plot based on the provided configuration.

        Args:
            config (dict): A dictionary containing the configuration for the gridded map plot.
            logger (Logger): An instance of the logger for logging messages.
            dataobj: An instance of the data object containing input data.

        This class initializes and configures a gridded map plot based on the provided
        configuration. The gridded map plot is created using a declarative plotting library from
        EMCPy (https://github.com/NOAA-EMC/emcpy).

        Example:

            ::

                    config = {
                        "longitude": {"variable": "collection::group::variable"},
                        "latitude": {"variable": "collection::group::variable"},
                        "data": {"variable": "collection::group::variable"},
                        "plot_property": "property_value",
                        "plot_option": "option_value",
                        "schema": "path_to_schema_file.yaml"
                    }
                    logger = Logger()
                    map_plot = MapGridded(config, logger, None)
        """
        self.collection = None
        self.datavar_name = None
        self.slice = None

        self.config = config
        self.logger = logger
        self.dataobj = dataobj
        self.lonvar = []
        self.latvar = []
        self.datavar = []
        self.plotobj = None

# --------------------------------------------------------------------------------------------------

    def data_prep(self):

        # prepare data based on config
        lonvar_cgv = self.config['longitude']['variable'].split('::')
        self.collection = lonvar_cgv[0]
        self.lonvar = self.dataobj.get_variable_data(lonvar_cgv[0], lonvar_cgv[1], lonvar_cgv[2], None)
        self.lonvar = slice_var_from_str(self.config['longitude'], self.lonvar, self.logger)
        latvar_cgv = self.config['latitude']['variable'].split('::')
        self.latvar = self.dataobj.get_variable_data(latvar_cgv[0], latvar_cgv[1], latvar_cgv[2], None)
        self.latvar = slice_var_from_str(self.config['latitude'], self.latvar, self.logger)
        datavar_cgv = self.config['data']['variable'].split('::')
        self.datavar_name = datavar_cgv[1] + '::' + datavar_cgv[2]
        self.datavar = self.dataobj.get_variable_data(datavar_cgv[0], datavar_cgv[1], datavar_cgv[2], None)
        self.datavar = slice_var_from_str(self.config['data'], self.datavar, self.logger)
        self.slice = self.config['data']['slices']

# --------------------------------------------------------------------------------------------------

    @abstractmethod
    def configure_plot(self):
        pass


