from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.contour_plot import ContourPlot

# --------------------------------------------------------------------------------------------------


class EmcpyContourPlot(ContourPlot):

    """
    EmcpyContourPlot class is a subclass of the ContourPlot class, designed for configuring
    and plotting contour plot visualizations using the emcpy library.

    Attributes:
        Inherits attributes from the ContourPlot class.

    Methods:
        configure_plot(): Configures the plotting settings for the contour plot.
    """

    def configure_plot(self):

        """
        Configures the plotting settings for the contour plot.

        Returns:
            plotobj: The configured plot object for emcpy contour plots.
        """

        # Create declarative plotting ContourPlot object
        # -------------------------------------------
        self.plotobj = emcpy.plots.plots.ContourPlot(self.xdata, self.ydata, self.z)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'contour_plot.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['x', 'y', 'z', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
