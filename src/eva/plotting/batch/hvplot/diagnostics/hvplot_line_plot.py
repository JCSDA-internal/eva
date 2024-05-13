from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import pandas as pd
import hvplot.pandas

from eva.plotting.batch.base.diagnostics.line_plot import LinePlot

# --------------------------------------------------------------------------------------------------


class HvplotLinePlot(LinePlot):

    def configure_plot(self):

        df = pd.DataFrame()
        df['x'] = self.xdata
        df['y'] = self.ydata

        line = df.hvplot.line(x='x', y='y', c=self.color, clabel=self.label)
        scatter = df.hvplot.scatter(x='x', y='y').opts(color=self.color, size=5, marker='o')
        self.plotobj = line * scatter

        return self.plotobj

# --------------------------------------------------------------------------------------------------
