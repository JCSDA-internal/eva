import os
import pandas as pd
import hvplot.pandas
import holoviews as hv
from scipy.stats import linregress

from eva.plotting.batch.base.diagnostics.density import Density

# --------------------------------------------------------------------------------------------------


class HvplotDensity(Density):

    def configure_plot(self):
        df = pd.DataFrame()
        df['data'] = self.data
        color = self.config['color']
        label = self.config['label']
        alpha = self.config['alpha']
        bw_adjust = self.config['bw_adjust']

        plotobj = df.hvplot.kde(filled=True, legend='top_left', alpha=alpha,
                                c=color, bandwidth=bw_adjust, label=label, height=400)

        return plotobj

# --------------------------------------------------------------------------------------------------                                                                        
