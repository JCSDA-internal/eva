from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import os
import pandas as pd
import hvplot.pandas
import holoviews as hv
from scipy.stats import linregress

from eva.plotting.batch.base.diagnostics.scatter import Scatter

# --------------------------------------------------------------------------------------------------


class HvplotScatter(Scatter):

    def configure_plot(self):
        # Save and access name of variables
        df = pd.DataFrame()
        df['xdata'] = self.xdata
        df['ydata'] = self.ydata
        color = self.config['color']
        size = self.config['markersize']
        label = self.config['label']

        # add line statistics to legend label
        try:
            plot_for_slope = df.hvplot.scatter('xdata', 'ydata')
            slope = hv.Slope.from_scatter(plot_for_slope).opts(color=color, line_width=1.5)
            slope_attrs = linregress(self.xdata, self.ydata)
            slope_expression = 'y='+f'{slope.slope:.3f}'+"x+"+f'{slope.y_intercept:.3f}'
            r_sq = ', r^2: ' + f'{slope_attrs.rvalue**2:.3f}'
            slope_label = "y="+f'{slope.slope:.3f}'+"x+"+f'{slope.y_intercept:.3f}'+r_sq
            plot = df.hvplot.scatter('xdata', 'ydata', width=600, height=600,
                                     s=size, c=color, label=label+", "+slope_label)
            new_plot = hv.Overlay([plot, plot])
            plotobj = new_plot * slope
            plotobj.opts(show_legend=False)
        except Exception:
            plot = df.hvplot.scatter('xdata', 'ydata', s=size, c=color, label=label)
            plotobj = hv.Overlay([plot, plot])
            plotobj.opts(show_legend=False)

        return plotobj

# --------------------------------------------------------------------------------------------------
