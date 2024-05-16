from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.scatter import Scatter

# --------------------------------------------------------------------------------------------------


class EmcpyScatter(Scatter):
    """
    EmcpyScatter class is a subclass of the Scatter class, specialized for
    configuring and plotting scatter visualizations using the emcpy library.

    Attributes:
        plotobj (object): A declarative plotting Scatter object specific to emcpy scatter plots.
        xdata (array-like): The x-data for the scatter plot.
        ydata (array-like): The y-data for the scatter plot.
        config (dict): Configuration settings for the plot.
        logger (Logger): Logger object for logging messages and errors.

    Methods:
        configure_plot(): Configures the plotting settings for the scatter plot.
    """
    def configure_plot(self):
        """
        Configures the plotting settings for the scatter plot.

        Returns:
            plotobj: The configured plot object for emcpy scatter plots.
        """
        # Create declarative plotting Scatter object
        # ------------------------------------------
        self.plotobj = emcpy.plots.plots.Scatter(self.xdata, self.ydata)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'scatter.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['x', 'y', 'type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
