from bokeh.plotting import save, output_file
from bokeh.embed import components # for pkl files
import pickle as pkl # for pkl files
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

    def add_text(self, xloc, yloc, text, transform='datacoords', **kwargs):

        if not hasattr(self, 'text'):
            self.text = []

        self.text.append({
            'xloc': xloc,
            'yloc': yloc,
            'text': text,
            'transform': transform,
            'kwargs': kwargs
        })

    def add_colorbar(self, label=None, fontsize=12, single_cbar=False,
                     cbar_location=None, **kwargs):

        kwargs.setdefault('orientation', 'horizontal')

        pad = 0.15 if kwargs['orientation'] == 'horizontal' else 0.1
        fraction = 0.065 if kwargs['orientation'] == 'horizontal' else 0.085

        kwargs.setdefault('pad', pad)
        kwargs.setdefault('fraction', fraction)

        if not cbar_location:
            h_loc = [0.14, -0.1, 0.8, 0.04]
            v_loc = [1.02, 0.12, 0.04, 0.8]
            cbar_location = h_loc if kwargs['orientation'] == 'horizontal' else v_loc

        self.colorbar = {
            'label': label,
            'fontsize': fontsize,
            'single_cbar': single_cbar,
            'cbar_loc': cbar_location,
            'kwargs': kwargs
        }

    def add_map_features(self, feature_list=['coastline']):

        self.map_features = feature_list


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
        item_list = []
        for plot_obj in self.plot_list:

            base_hvplot = holoviews.Scatter([], [])
            for layer in plot_obj.plot_layers:
                # Combine layers if necessary
                base_hvplot = base_hvplot * layer

            self.fig = base_hvplot
            for feat in vars(plot_obj).keys():
                self._plot_features(plot_obj, feat)

            new_plot_list.append(self.fig)

            # Keep track of text found in plot object
            if hasattr(plot_obj, 'text'):
                colors_list = [text_dict['kwargs']['color'] for text_dict in plot_obj.text]
                stats_list = [text_dict['text'] for text_dict in plot_obj.text]
                hv_text = holoviews.Table({'Color': colors_list, 'Statistics': stats_list},
                                          ['Color', 'Statistics'])
                hv_text.opts(width=1000)
                item_list.append(hv_text)

        # Construct subplots if necessary
        if len(new_plot_list) == 1:
            self.fig = new_plot_list[0]
        else:
            # use layout to construct subplot
            self.fig = holoviews.Layout(new_plot_list).cols(self.ncols)
            self.fig.opts(shared_axes=False)

        # Add any text that was found in the plot_list
        # combine self.fig and text list into one list
        final_list = [self.fig] + item_list
        self.fig = holoviews.Layout(final_list).cols(1)

    def add_suptitle(self, text, **kwargs):
        self.fig.opts(title=text)

    def save_figure(self, pathfile, **kwargs):
        pathfile_dir = os.path.dirname(pathfile)
        if not os.path.exists(pathfile_dir):
            os.makedirs(pathfile_dir)
        bokeh_fig = hv.render(self.fig, backend='bokeh')
        
	# Eventually make this part optional
        script, div = components(bokeh_fig)
        save_dict = {'div' : div, 'script' : script}
        with open(pathfile, 'wb') as f:
            pkl.dump(save_dict, f)

        #output_file(pathfile)
        #save(bokeh_fig)
        #holoviews.save(self.fig, pathfile, backend="bokeh")

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
