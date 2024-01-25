from bokeh.plotting import save, output_file
from bokeh.layouts import gridplot
import panel as pn
import holoviews
import hvplot as hv
import os


class CreatePlot:

    def __init__(self, plot_layers=[], projection=None, domain=None):
        self.plot_layers = plot_layers
        if projection:
            self.projection = projection
        if domain:
            self.domain = domain

    def add_grid(self, **kwargs):
        self.grid = {
            **kwargs
        }

    def add_legend(self, **kwargs):
        self.legend = {
            **kwargs
        }

    def add_xlabel(self, xlabel, labelpad=None,
                   loc='center', **kwargs):
        self.xlabel = {
            'xlabel': xlabel,
            'labelpad': labelpad,
            'loc': loc,
            **kwargs
        }

    def add_ylabel(self, ylabel, labelpad=None,
                   loc='center', **kwargs):
        self.ylabel = {
            'ylabel': ylabel,
            'labelpad': labelpad,
            'loc': loc,
            **kwargs
        }


class CreateFigure:
  
    def __init__(self, nrows=1, ncols=1, figsize=(8, 6)):
        self.nrows = nrows
        self.ncols = ncols
        self.figsize = figsize
        self.plot_list = []
        self.fig = None
        self.subplot_row = None

    def create_figure(self):

        new_plot_list = []
        for plot_obj in self.plot_list:

            base_hvplot = holoviews.Scatter([], [])
            for layer in plot_obj.plot_layers:
                # combine layers if necessary
                base_hvplot = base_hvplot * layer

            self.fig = base_hvplot
            for feat in vars(plot_obj).keys():
                self._plot_features(plot_obj, feat)

            new_plot_list.append(self.fig)

        # Construct subplots if necessary
        if len(new_plot_list) == 1:
            self.fig = new_plot_list[0]
        else:
            # use layout to construct subplot
            self.fig = holoviews.Layout(new_plot_list).cols(self.ncols)
            self.fig.opts(shared_axes=False)            

    def add_suptitle(self, text, **kwargs):
        self.fig.opts(title=text)

    def save_figure(self, pathfile, **kwargs):
        pathfile_dir = os.path.dirname(pathfile)
        if not os.path.exists(pathfile_dir):
            os.makedirs(pathfile_dir)
        holoviews.save(self.fig, pathfile, backend="bokeh")

    def close_figure(self):
        pass

    def _plot_features(self, plot_obj, feature):

        feature_dict = {
            'xlabel': self._plot_xlabel,
            'ylabel': self._plot_ylabel,
            'legend': self._plot_legend,
            'grid': self._plot_grid,
        }

        if feature in feature_dict:
            feature_dict[feature](vars(plot_obj)[feature])

    def _plot_grid(self, grid):
        self.fig.opts(show_grid=True)

    def _plot_xlabel(self, xlabel):
        self.fig.opts(xlabel=xlabel['xlabel'])

    def _plot_ylabel(self, ylabel):
        self.fig.opts(ylabel=ylabel['ylabel'])

    def _plot_legend(self, legend):
        self.fig.opts(legend_position='top_left', show_legend=True)
