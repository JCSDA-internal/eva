from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.map_plots
import os

from eva.plotting.batch.base.diagnostics.map_contour import MapContour

# --------------------------------------------------------------------------------------------------


class EmcpyMapContour(MapContour):
    """
    EmcpyMapContour class is a subclass of the MapContour class, tailored for
    configuring and plotting contour map visualizations using the emcpy library.

    Attributes:
        Inherits attributes from the MapContour class.

    Methods:
        configure_plot(): Configures the plotting settings for the contour map.
    """

    def configure_plot(self):
        """
        Configures the plotting settings for the contour map.

        Returns:
            plotobj: The configured plot object for emcpy contour maps.
        """

        # Create declarative plotting MapContour object
        self.plotobj = emcpy.plots.map_plots.MapContour(self.latvar, self.lonvar, self.datavar)
        # get defaults from schema
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'map_contour.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['longitude', 'latitude', 'data', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)
        return self.plotobj

# --------------------------------------------------------------------------------------------------
