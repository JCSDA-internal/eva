import pandas as pd
import hvplot.pandas

from eva.plotting.batch.base.diagnostics.histogram import Histogram

# --------------------------------------------------------------------------------------------------


class HvplotHistogram(Histogram):
    """
    Subclass of Histogram for generating histograms using hvplot.

    Attributes:
        Inherits attributes from the Histogram class.
    """
    def configure_plot(self):
        """
        Configures and generates a histogram plot using hvplot.

        Returns:
            plotobj: plot object representing the generated histogram plot.
        """
        df = pd.DataFrame()
        df["var"] = self.data
        self.plotobj = df.hvplot.hist(bins=self.config['bins'], color=self.config['color'],
                                      label=self.config['label'], height=600, width=600,
                                      legend='top_left')

        return self.plotobj

# --------------------------------------------------------------------------------------------------
