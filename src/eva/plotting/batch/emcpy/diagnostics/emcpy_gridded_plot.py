from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.gridded_plot import GriddedPlot

# --------------------------------------------------------------------------------------------------


class EmcpyGriddedPlot(GriddedPlot):

    """
    EmcpyGriddedPlot class inherits from the GriddedPlot class and provides methods
    to configure plotting settings for gridded plots using the emcpy library.

    Attributes:
        Inherits attributes from the GriddedPlot class.

    Methods:
        configure_plot(): Configures the plotting settings for the gridded plot.
    """

    def configure_plot(self):

        """
        Configures the plotting settings for the gridded plot.

        Returns:
            plotobj: Plotting object configured with the specified settings.
        """

        # Create declarative plotting density object
        # --------------------------------------------
        self.plotobj = emcpy.plots.plots.GriddedPlot(self.xdata, self.ydata, self.zdata)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'gridded_plot.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['x', 'y', 'z', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
