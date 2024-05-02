from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.line_plot import LinePlot

# --------------------------------------------------------------------------------------------------

class EmcpyLinePlot(LinePlot):

    def configure_plot(self):

        # Create declarative plotting LinePlot object
        # -------------------------------------------
        self.plotobj = emcpy.plots.plots.LinePlot(self.xdata, self.ydata)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'batch', 'emcpy', 'defaults',
                                                         'line_plot.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['x', 'y', 'type', 'schema', 'channel', 'level', 'datatype']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
