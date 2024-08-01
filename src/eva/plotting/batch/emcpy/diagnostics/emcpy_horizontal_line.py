from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.horizontal_line import HorizontalLine

# --------------------------------------------------------------------------------------------------


class EmcpyHorizontalLine(HorizontalLine):

    """
    EmcpyHorizontalLine class is a subclass of the HorizontalLine class, designed for
    configuring and plotting horizontal line visualizations using the emcpy library.

    Attributes:
        Inherits attributes from the HorizontalLine class.

    Methods:
        configure_plot(): Configures the plotting settings for the horizontal line.
    """

    def configure_plot(self):

        """
        Configures the plotting settings for the horizontal line.

        Returns:
            plotobj: The configured plot object for emcpy horizontal lines.
        """

        # Create declarative plotting HorizontalLine object
        # -------------------------------------------
        self.plotobj = emcpy.plots.plots.HorizontalLine(self.yval)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'horizontal_line.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['type', 'schema']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
