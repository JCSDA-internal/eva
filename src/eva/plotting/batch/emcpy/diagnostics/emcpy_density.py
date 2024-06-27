from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.plots
import os

from eva.plotting.batch.base.diagnostics.density import Density

# --------------------------------------------------------------------------------------------------


class EmcpyDensity(Density):

    """
    EmcpyDensity class inherits from the Density class and provides methods
    to configure plotting settings for density plots using the emcpy library.

    Attributes:
        Inherits attributes from the Density class.

    Methods:
        configure_plot(): Configures the plotting settings for the density plot.
    """

    def configure_plot(self):

        """
        Configures the plotting settings for the density plot.

        Returns:
            plotobj: Plotting object configured with the specified settings.
        """

        # Create declarative plotting density object
        # --------------------------------------------
        self.plotobj = emcpy.plots.plots.Density(self.data)

        # Get defaults from schema
        # ------------------------
        layer_schema = self.config.get('schema', os.path.join(return_eva_path(), 'plotting',
                                       'batch', 'emcpy', 'defaults', 'density.yaml'))
        new_config = get_schema(layer_schema, self.config, self.logger)
        delvars = ['type', 'schema', 'data']
        for d in delvars:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
