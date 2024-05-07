from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import os
import holoviews as hv

from eva.plotting.batch.base.diagnostics.horizontal_line import HorizontalLine

# --------------------------------------------------------------------------------------------------


class HvplotHorizontalLine(HorizontalLine):

    def configure_plot(self):

        self.plotobj = hv.HLine(self.yval).opts(color='black', line_width=self.config['linewidth'])
        return self.plotobj

# --------------------------------------------------------------------------------------------------
