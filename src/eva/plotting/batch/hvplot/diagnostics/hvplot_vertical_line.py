from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import os
import pandas as pd
import hvplot.pandas
import holoviews as hv
from scipy.stats import linregress

from eva.plotting.batch.base.diagnostics.vertical_line import VerticalLine

# --------------------------------------------------------------------------------------------------


class HvplotVerticalLine(VerticalLine):

    def configure_plot(self):

        self.plotobj = hv.VLine(self.xval).opts(color='black', line_width=self.config['linewidth'])
        return self.plotobj

# --------------------------------------------------------------------------------------------------
