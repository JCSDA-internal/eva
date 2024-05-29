import os
import pandas as pd
import hvplot.pandas
import holoviews as hv
from bokeh.models import HoverTool

from eva.plotting.batch.base.diagnostics.density import Density

# --------------------------------------------------------------------------------------------------


class HvplotDensity(Density):
    """
    Subclass of Density for generating density plots using hvplot backend.

    Attributes:
        Inherits attributes from the Density class.
    """

    def configure_plot(self):
        """
        Configures and generates a density plot using hvplot backend.

        Returns:
            plotobj: plot object representing the generated density plot.
        """
        df = pd.DataFrame()
        df['data'] = self.data
        color = self.config['color']
        label = self.config['label']

        hover = HoverTool(tooltips=[('data', '$data')])
        plotobj = df.hvplot.kde(filled=True, legend='top_left', color=color,
                                tools=[hover], label=label, height=600, width=600)

        return plotobj

# --------------------------------------------------------------------------------------------------
