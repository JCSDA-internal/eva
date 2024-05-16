import holoviews as hv
from eva.plotting.batch.base.diagnostics.horizontal_line import HorizontalLine

# --------------------------------------------------------------------------------------------------


class HvplotHorizontalLine(HorizontalLine):

    def configure_plot(self):

        self.plotobj = hv.HLine(self.yval).opts(color='black', line_width=self.config['linewidth'])
        return self.plotobj

# --------------------------------------------------------------------------------------------------
