from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object
import eva.plot_tools.plots
import os

class Scatter():


    def __init__(self, config, dataobj):
        # prepare data based on config
        varnames = config['comparison']
        xdata = dataobj.data[varnames[0]].to_numpy()
        ydata = dataobj.data[varnames[1]].to_numpy()
        # create declarative plotting Scatter object
        self.plotobj = eva.plot_tools.plots.Scatter(xdata, ydata)
        # get defaults from schema
        layer_schema = config.get("schema",
                                  os.path.join(return_eva_path(),
                                               'defaults',
                                               'scatter.yaml'))
        config = get_schema(layer_schema, config, dataobj.logger)
        delvars = ['comparison', 'type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, dataobj.logger)
