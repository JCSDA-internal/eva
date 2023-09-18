from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import emcpy.plots.plots
import os
import numpy as np

from eva.plotting.batch.base.diagnostics.scatter import Scatter

# --------------------------------------------------------------------------------------------------


class EmcpyScatter(Scatter):

    def configure_plot(self):

        # Create declarative plotting Scatter object
        # ------------------------------------------
        self.plotobj = emcpy.plots.plots.Scatter(self.xdata, self.ydata)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'emcpy', 'defaults', 'scatter.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['x', 'y', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
