import os
import pandas as pd
import hvplot.pandas
import holoviews as hv
from scipy.stats import linregress
from bokeh.models import HoverTool

from eva.plotting.batch.base.diagnostics.density import Density

# --------------------------------------------------------------------------------------------------


class HvplotDensity(Density):

    def configure_plot(self):
        df = pd.DataFrame()
        df['data'] = self.data
        color = self.config['color']
        label = self.config['label']

        hover = HoverTool(tooltips=[('data', '$data')])
        plotobj = df.hvplot.kde(filled=True, legend='top_left', color=color,
                                tools=[hover], label=label, height=600, width=600)

        return plotobj

# --------------------------------------------------------------------------------------------------
