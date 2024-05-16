import pandas as pd
import hvplot.pandas
from eva.plotting.batch.base.diagnostics.line_plot import LinePlot

# --------------------------------------------------------------------------------------------------


class HvplotLinePlot(LinePlot):
    """
    Subclass of LinePlot for generating line plots using hvplot.

    Attributes:
        Inherits attributes from the LinePlot class.
    """
    def configure_plot(self):
        """
        Configures and generates a line plot using hvplot.

        Returns:
            plotobj: plot object representing the generated line plot.
        """
        df = pd.DataFrame()
        df['x'] = self.xdata
        df['y'] = self.ydata

        line = df.hvplot.line(x='x', y='y', c=self.color, clabel=self.label)
        scatter = df.hvplot.scatter(x='x', y='y').opts(color=self.color, size=5, marker='o')
        self.plotobj = line * scatter

        return self.plotobj

# --------------------------------------------------------------------------------------------------
