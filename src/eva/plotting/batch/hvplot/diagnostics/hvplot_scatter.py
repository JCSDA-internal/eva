from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import os
#import hvplot
import pandas as pd
import hvplot.pandas

from eva.plotting.batch.base.diagnostics.scatter import Scatter

# --------------------------------------------------------------------------------------------------


class HvplotScatter(Scatter):

    def configure_plot(self):
        # Save and access name of variables
        df = pd.DataFrame()
        df['xdata'] = self.xdata
        df['ydata'] = self.ydata
        self.plotobj =  df.hvplot.scatter('xdata', 'ydata', s=20, c='b', height=400, width=400)
        return self.plotobj

# --------------------------------------------------------------------------------------------------
