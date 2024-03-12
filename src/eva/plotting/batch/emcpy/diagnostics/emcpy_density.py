from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.density import Density

# --------------------------------------------------------------------------------------------------


class EmcpyDensity(Density):

    def configure_plot(self):

        # Create declarative plotting density object
        # --------------------------------------------
        self.plotobj = emcpy.plots.plots.Density(self.data)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                         'emcpy', 'defaults', 'density.yaml'))
        config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['type', 'schema', 'data']
        for d in delvars:
            self.config.pop(d, None)
        self.plotobj = update_object(self.plotobj, self.config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
