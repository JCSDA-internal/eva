from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.histogram import Histogram

# --------------------------------------------------------------------------------------------------


class EmcpyHistogram(Histogram):

    """
    EmcpyHistogram class is a subclass of the Histogram class, tailored for configuring
    and plotting histogram visualizations using the emcpy library.

    Attributes:
        plotobj (object): A declarative plotting histogram object specific to emcpy histograms.
        data (object): Data object to be used for plotting.
        config (dict): Configuration settings for the plot.
        logger (Logger): Logger object for logging messages and errors.

    Methods:
        configure_plot(): Configures the plotting settings for the histogram.
    """

    def configure_plot(self):

        """
        Configures the plotting settings for the histogram.

        Returns:
            plotobj: The configured plot object for EMCpy histograms.
        """

        # Create declarative plotting histogram object
        # --------------------------------------------
        self.plotobj = emcpy.plots.plots.Histogram(self.data)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'histogram.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['type', 'schema', 'data']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
