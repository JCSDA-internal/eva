from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import eva.plot_tools.plots
import os


class Scatter():

    def __init__(self, config, logger, dataobj):
        # prepare data based on config
        # for scatter it needs to be flattened, but can be sliced too
        xvar = dataobj.get_variable_data(config['x']['variable'])
        xvar = slice_var_from_str(config['x'], xvar, logger)
        xdata = xvar.flatten()
        yvar = dataobj.get_variable_data(config['y']['variable'])
        yvar = slice_var_from_str(config['y'], yvar, logger)
        ydata = yvar.flatten()
        # create declarative plotting Scatter object
        self.plotobj = eva.plot_tools.plots.Scatter(xdata, ydata)
        # get defaults from schema
        layer_schema = config.get("schema",
                                  os.path.join(return_eva_path(),
                                               'defaults',
                                               'scatter.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['x', 'y', 'type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)
