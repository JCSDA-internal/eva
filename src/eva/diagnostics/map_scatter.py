from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import eva.plot_tools.plots
import os


class MapScatter():

    def __init__(self, config, logger, dataobj):
        # prepare data based on config
        # Optionally get the channel to plot
        channel = None
        if 'channel' in config['data']:
            channel = config['data'].get('channel')
        lonvar_cgv = config['longitude']['variable'].split('::')
        lonvar = dataobj.get_variable_data(lonvar_cgv[0], lonvar_cgv[1], lonvar_cgv[2], None)
        lonvar = slice_var_from_str(config['longitude'], lonvar, logger)
        latvar_cgv = config['latitude']['variable'].split('::')
        latvar = dataobj.get_variable_data(latvar_cgv[0], latvar_cgv[1], latvar_cgv[2], None)
        latvar = slice_var_from_str(config['latitude'], latvar, logger)
        datavar_cgv = config['data']['variable'].split('::')
        datavar = dataobj.get_variable_data(datavar_cgv[0], datavar_cgv[1], datavar_cgv[2], channel)
        datavar = slice_var_from_str(config['data'], datavar, logger)
        # scatter data should be flattened
        lonvar = lonvar.flatten()
        latvar = latvar.flatten()
        datavar = datavar.flatten()
        # create declarative plotting MapScatter object
        self.plotobj = eva.plot_tools.plots.MapScatter(latvar, lonvar, datavar)
        # get defaults from schema
        layer_schema = config.get("schema",
                                  os.path.join(return_eva_path(),
                                               'defaults',
                                               'map_scatter.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['longitude', 'latitude', 'data', 'type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)
