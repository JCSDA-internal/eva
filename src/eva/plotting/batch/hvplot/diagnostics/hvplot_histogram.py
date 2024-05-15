from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import os
import pandas as pd
import hvplot.pandas
import holoviews as hv
from scipy.stats import linregress

from eva.plotting.batch.base.diagnostics.histogram import Histogram

# --------------------------------------------------------------------------------------------------


class HvplotHistogram(Histogram):

    def configure_plot(self):

        df = pd.DataFrame()
        df["var"] = self.data
        self.plotobj = df.hvplot.hist(bins=self.config['bins'], color=self.config['color'],
                                      label=self.config['label'], height=600, width=600,
                                      legend='top_left')

        return self.plotobj

# --------------------------------------------------------------------------------------------------
