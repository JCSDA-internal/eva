from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.map_scatter import MapScatter

# --------------------------------------------------------------------------------------------------

class EmcpyMapScatter(MapScatter):

    def configure_plot(self):

        # create declarative plotting MapScatter object
        self.plotobj = emcpy.plots.map_plots.MapScatter(self.latvar, self.lonvar, self.datavar)
        # get defaults from schema
        layer_schema = self.config.get("schema",
                                  os.path.join(return_eva_path(),
                                               'plotting',
                                               'emcpy', 'defaults',
                                               'map_scatter.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['longitude', 'latitude', 'data', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
