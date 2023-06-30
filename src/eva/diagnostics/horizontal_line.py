from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os


class HorizontalLine():

    def __init__(self, config, logger, dataobj):

        # Get the y value to plot
        # -----------------------
        yval = config['y']

        # Create declarative plotting HorizontalLine object
        # -------------------------------------------
        self.plotobj = emcpy.plots.plots.HorizontalLine(yval)

        # Get defaults from schema
        # ------------------------
        layer_schema = config.get('schema', os.path.join(return_eva_path(), 'defaults',
                                  'horizontal_line.yaml'))
        config = get_schema(layer_schema, config, logger)
        delvars = ['type', 'schema']
        for d in delvars:
            config.pop(d, None)
        self.plotobj = update_object(self.plotobj, config, logger)
