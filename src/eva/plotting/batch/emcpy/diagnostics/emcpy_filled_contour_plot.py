from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.filled_contour_plot import FilledContourPlot

# --------------------------------------------------------------------------------------------------


class EmcpyFilledContourPlot(FilledContourPlot):

    """
    EmcpyFilledContourPlot class is a subclass of the FilledContourPlot class, designed for
    configuring and plotting filled contour plot visualizations using the emcpy library.

    Attributes:
        Inherits attributes from the FilledContourPlot class.

    Methods:
        configure_plot(): Configures the plotting settings for the filled contour plot.
    """

    def configure_plot(self):

        """
        Configures the plotting settings for the filled contour plot.

        Returns:
            plotobj: The configured plot object for emcpy filled contour plots.
        """

        # Create declarative plotting FilledContourPlot object
        # ----------------------------------------------------
        self.plotobj = emcpy.plots.plots.FilledContourPlot(self.xdata, self.ydata, self.z)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'filled_contour_plot.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['x', 'y', 'z', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
