# This work developed by NOAA/NWS/EMC under the Apache 2.0 license.
import numpy as np

__all__ = ['Scatter', 'Histogram', 'Density', 'LinePlot' 'VerticalLine',
           'HorizontalLine', 'BarPlot' 'HorizontalBar',
           'MapScatter', 'MapGridded', 'MapContour']


class Scatter():

    def __init__(self, x, y):
        """
        Constructor for Scatter.
        Args:
            x : (array type)
            y : (array type)
        """

        super().__init__()
        self.plottype = 'scatter'

        self.x = x
        self.y = y

        self.markersize = 5
        self.color = 'darkgray'
        self.marker = 'o'
        self.vmin = None
        self.vmax = None
        self.alpha = None
        self.linewidths = 1.5
        self.edgecolors = None
        self.label = f'n={np.count_nonzero(~np.isnan(x))}'
        self.do_linear_regression = True

    def add_linear_regression(self):
        """
        Include linear regression line info as attributes.
        """
        self.linear_regression = {
            'color': 'black',
            'linewidth': 1,
            'linestyle': '-'
        }

    def density_scatter(self):
        """
        Include density scatter plot info as attributes.
        """
        self.density = {
            'sort': True,
            'cmap': 'nipy_spectral_r',
            'colorbar': True,
            'bins': [100, 100],
            'interp': 'linear',
            'nsamples': True
        }


class Histogram():

    def __init__(self, data):
        """
        Constructor for Histogram.
        Args:
            data : (array type)
        """

        super().__init__()
        self.plottype = 'histogram'

        self.data = data

        self.bins = 10
        self.range = None
        self.density = False
        self.weights = None
        self.cumulative = False
        self.bottom = None
        self.histtype = 'bar'
        self.align = 'mid'
        self.orientation = 'vertical'
        self.rwidth = None
        self.log = False
        self.color = 'tab:blue'
        self.label = f'n={np.count_nonzero(~np.isnan(data))}'
        self.stacked = False
        self.alpha = None


class Density():

    def __init__(self, data):
        """
        Constructor for Density.
        Args:
            data : (array type)
        """

        super().__init__()
        self.plottype = 'density'

        self.data = data

        self.bins = 10
        self.range = None
        self.density = False
        self.weights = None
        self.cumulative = False
        self.bottom = None
        self.align = 'mid'
        self.orientation = 'vertical'
        self.rwidth = None
        self.log = False
        self.color = 'tab:blue'
        self.label = f'n={np.count_nonzero(~np.isnan(data))}'
        self.stacked = False
        self.alpha = None


class LinePlot():

    def __init__(self, x, y):
        """
        Constructor for LinePlot.
        Args:
            x : (array type)
            y : (array type)
        """
        super().__init__()
        self.plottype = 'line_plot'

        self.x = x
        self.y = y

        self.color = 'tab:blue'
        self.linestyle = '-'
        self.linewidth = 1.5
        self.marker = None
        self.markersize = None
        self.alpha = None
        self.label = None


class VerticalLine():

    def __init__(self, x):
        """
        Constructor for VerticalLine
        Args:
            x : (int/float) x-value where vertical line
                is to be plotted
        """

        super().__init__()
        self.plottype = 'vertical_line'

        self.x = x

        self.color = 'black'
        self.linestyle = '-'
        self.linewidth = 1.5
        self.label = None


class HorizontalLine():

    def __init__(self, y):
        """
        Constructor for HorizontalLine
        Args:
            y : (int/float) y-value where horizontal
                line is to be plotted
        """

        super().__init__()
        self.plottype = 'horizontal_line'

        self.y = y

        self.color = 'black'
        self.linestyle = '-'
        self.linewidth = 1.5
        self.label = None


class BarPlot():

    def __init__(self, x, height):
        """
        Constructor for BarPlot.
        Args:
            x : (array type) x coordinate of bars
            height : (array type) the height(s) of the bars
        """

        super().__init__()
        self.plottype = 'bar_plot'

        self.x = x
        self.height = height

        self.width = 0.8
        self.bottom = 0
        self.align = 'center'
        self.color = 'tab:blue'
        self.edgecolor = None
        self.linewidth = 0
        self.tick_label = None
        self.xerr = None
        self.yerr = None
        self.ecolor = 'black'
        self.capsize = 0
        self.error_kw = {}
        self.log = False


class HorizontalBar():

    def __init__(self, y, width):
        """
        Constructor to create a horizontal bar plot.
        Args:
            y : (array type) y coordinate of bars
            width : (array type) the width(s) of the bars
        """

        super().__init__()
        self.plottype = 'horizontal_bar'

        self.y = y
        self.width = width

        self.height = 0.8
        self.left = 0
        self.align = 'center'
        self.color = 'tab:blue'
        self.edgecolor = None
        self.linewidth = 0
        self.tick_label = None
        self.xerr = None
        self.yerr = None
        self.ecolor = 'black'
        self.capsize = 0
        self.error_kw = {}
        self.log = False


class MapScatter:

    def __init__(self, latitude, longitude, data=None):
        """
        Constructor for MapScatter.
        Args:
            latitude : (array type) Latitude data
            longitude : (array type) Longitude data
            data : (array type; default=None) data to be plotted
        """
        self.plottype = 'map_scatter'

        self.latitude = latitude
        self.longitude = longitude
        self.data = data

        self.marker = 'o'
        self.markersize = 5
        if data is None:
            self.color = 'tab:blue'
        else:
            self.cmap = 'viridis'
        self.linewidths = 1.5
        self.edgecolors = None
        self.alpha = None
        self.vmin = None
        self.vmax = None
        self.label = None
        self.colorbar = None


class MapGridded:

    def __init__(self, latitude, longitude, data):
        """
        Constructor for MapGridded.
        Args:
            latitude : (array type) Latitude data
            longitude : (array type) Longitude data
            data : (array type) data to be plotted
        """
        self.plottype = 'map_gridded'

        self.latitude = latitude
        self.longitude = longitude
        self.data = data

        self.cmap = 'viridis'
        self.vmin = None
        self.vmax = None
        self.alpha = None


class MapContour:

    def __init__(self, latitude, longitude, data):
        """
        Constructor for MapScatter.
        Args:
            latitude : (array type) Latitude data
            longitude : (array type) Longitude data
            data : (array type) data to be plotted
        """
        self.plottype = 'map_contour'

        self.latitude = latitude
        self.longitude = longitude
        self.data = data

        self.levels = None
        self.clabel = False
        self.colors = 'black'
        self.linewidths = 1.5
        self.linestyles = '-'
        self.cmap = None
        self.vmin = None
        self.vmax = None
        self.alpha = None
