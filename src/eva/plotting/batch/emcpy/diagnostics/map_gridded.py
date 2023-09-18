from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import emcpy.plots.map_plots
import os


# --------------------------------------------------------------------------------------------------


class MapGridded():

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

        # prepare data based on config
        lonvar_cgv = config['longitude']['variable'].split('::')
        lonvar = dataobj.get_variable_data(lonvar_cgv[0], lonvar_cgv[1], lonvar_cgv[2], None)
        lonvar = slice_var_from_str(config['longitude'], lonvar, logger)
        latvar_cgv = config['latitude']['variable'].split('::')
        latvar = dataobj.get_variable_data(latvar_cgv[0], latvar_cgv[1], latvar_cgv[2], None)
        latvar = slice_var_from_str(config['latitude'], latvar, logger)
        datavar_cgv = config['data']['variable'].split('::')
        datavar = dataobj.get_variable_data(datavar_cgv[0], datavar_cgv[1], datavar_cgv[2], None)
        datavar = slice_var_from_str(config['data'], datavar, logger)

        # create declarative plotting MapGridded object
        self.plotobj = emcpy.plots.map_plots.MapGridded(latvar, lonvar, datavar)
        # get defaults from schema
        layer_schema = config.get("schema",
                                  os.path.join(return_eva_path(),
                                               'plotting',
                                               'emcpy', 'defaults',
                                               'map_gridded.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['longitude', 'latitude', 'data', 'type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)


# --------------------------------------------------------------------------------------------------
