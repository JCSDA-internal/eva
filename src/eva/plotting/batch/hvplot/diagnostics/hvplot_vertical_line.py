import holoviews as hv
from eva.plotting.batch.base.diagnostics.vertical_line import VerticalLine

# --------------------------------------------------------------------------------------------------


class HvplotVerticalLine(VerticalLine):
    """
    Subclass of VerticalLine for generating vertical line plots using hvplot.

    Attributes:
        Inherits attributes from the VerticalLine class.
    """
    def configure_plot(self):
        """
        Configures and generates a vertical line plot using hvplot.

        Returns:
            plotobj: plot object representing the generated vertical line plot.
        """
        self.plotobj = hv.VLine(self.xval).opts(color='black', line_width=self.config['linewidth'])
        return self.plotobj

# --------------------------------------------------------------------------------------------------
