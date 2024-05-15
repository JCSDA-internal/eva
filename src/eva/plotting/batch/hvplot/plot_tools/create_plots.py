from bokeh.plotting import save, output_file
from bokeh.embed import components # for pkl files
import pickle as pkl # for pkl files
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

    def create_figure(self):
        # Needs work, need to combine all the layers
        # and figure out how subplots will work
        self.fig = self.plot_list[0].plot_layers[0]
        plot_obj = self.plot_list[0]

        # Add all features to the figure
        for feat in vars(plot_obj).keys():
            self._plot_features(plot_obj, feat)

    def add_suptitle(self, text, **kwargs):
        self.fig.opts(title=text)

    def save_figure(self, pathfile, **kwargs):
        pathfile_dir = os.path.dirname(pathfile)
        if not os.path.exists(pathfile_dir):
            os.makedirs(pathfile_dir)
        bokeh_fig = hv.render(self.fig, backend='bokeh')
        
	# Eventually make this part optional
        script, div = components(plot)
        save_dict = {'div' : div, 'script' : script}
        with open(pathfile, 'wb') as f:
            pkl.dump(save_dict, f)

        #output_file(pathfile)
        #save(bokeh_fig)

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
