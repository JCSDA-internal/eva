from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.horizontal_line import HorizontalLine

# --------------------------------------------------------------------------------------------------

class EmcpyHorizontalLine(HorizontalLine):

    def configure_plot(self):

        # Create declarative plotting HorizontalLine object
        # -------------------------------------------
        self.plotobj = emcpy.plots.plots.HorizontalLine(self.yval)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'emcpy', 'defaults',
                                                         'horizontal_line.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, self.config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
