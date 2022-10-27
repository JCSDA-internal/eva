from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import emcpy.plots.plots
import os


class MapGridded():

    def __init__(self, config, logger, dataobj):
        # prepare data based on config
        lonvar = dataobj.get_variable_data(config['longitude']['variable'])
        lonvar = slice_var_from_str(config['longitude'], lonvar, logger)
        latvar = dataobj.get_variable_data(config['latitude']['variable'])
        latvar = slice_var_from_str(config['latitude'], latvar, logger)
        datavar = dataobj.get_variable_data(config['data']['variable'])
        datavar = slice_var_from_str(config['data'], datavar, logger)
        # create declarative plotting MapGridded object
        self.plotobj = emcpy.plots.plots.MapGridded(lonvar, latvar, datavar)
        # get defaults from schema
        layer_schema = config.get("schema",
                                  os.path.join(return_eva_path(),
                                               'defaults',
                                               'map_gridded.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['longitude', 'latitude', 'data', 'type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)
