from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import os
import pandas as pd
import hvplot.pandas

from eva.plotting.batch.base.diagnostics.horizontal_line import HorizontalLine

# --------------------------------------------------------------------------------------------------


class HvplotHorizontalLine(HorizontalLine):

    def configure_plot(self):
        df = pd.DataFrame()
        df['y'] = self.yval

        self.plotobj = df.hvplot.line(y='y')

        return self.plotobj

# --------------------------------------------------------------------------------------------------
