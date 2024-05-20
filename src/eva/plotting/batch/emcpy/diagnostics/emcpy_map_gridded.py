from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.map_plots
import os

from eva.plotting.batch.base.diagnostics.map_gridded import MapGridded

# --------------------------------------------------------------------------------------------------


class EmcpyMapGridded(MapGridded):
    """
    EmcpyMapGridded class is a subclass of the MapGridded class, tailored for
    configuring and plotting gridded map visualizations using the emcpy library.

    Attributes:
        Inherits attributes from the MapGridded class.

    Methods:
        configure_plot(): Configures the plotting settings for the gridded map.
    """

    def configure_plot(self):
        """
        Configures the plotting settings for the gridded map.

        Returns:
            plotobj: The configured plot object for emcpy gridded maps.
        """

        # create declarative plotting MapGridded object
        self.plotobj = emcpy.plots.map_plots.MapGridded(self.latvar, self.lonvar, self.datavar)
        # get defaults from schema
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'map_gridded.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['longitude', 'latitude', 'data', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)
        return self.plotobj

# --------------------------------------------------------------------------------------------------
