from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.map_plots
import os

from eva.plotting.batch.base.diagnostics.map_scatter import MapScatter

# --------------------------------------------------------------------------------------------------


class EmcpyMapScatter(MapScatter):
    """
    EmcpyMapScatter class is a subclass of the MapScatter class, designed for
    configuring and plotting scatter map visualizations using the emcpy library.

    Attributes:
        plotobj (object): A declarative plotting MapScatter object specific to emcpy scatter maps.
        latvar (array-like): Latitude variable for the scatter map.
        lonvar (array-like): Longitude variable for the scatter map.
        datavar (array-like): Data variable for the scatter map.
        config (dict): Configuration settings for the plot.
        logger (Logger): Logger object for logging messages and errors.

    Methods:
        configure_plot(): Configures the plotting settings for the scatter map.
    """

    def configure_plot(self):
        """
        Configures the plotting settings for the scatter map.

        Returns:
            plotobj: The configured plot object for emcpy scatter maps.
        """

        self.plotobj = emcpy.plots.map_plots.MapScatter(self.latvar, self.lonvar, self.datavar)
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'map_scatter.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['longitude', 'latitude', 'data', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
