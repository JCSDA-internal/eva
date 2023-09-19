from bokeh.plotting import save
import hvplot as hv
import os

class CreatePlot:

    def __init__(self, plot_layers=[], projection=None, domain=None):
        self.plot_layers = plot_layers
        if projection:
            self.projection = projection
        if domain:
            self.domain = domain

    def add_grid(self):
        pass

    def add_legend(self, **kwargs):
        self.legend = {
            **kwargs
        }

    def add_title(self, label, loc='center',
                  pad=None, **kwargs):

        self.title = {
            'label': label,
            'loc': loc,
            'pad': pad,
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

    def add_stats_dict(self, stats_dict={}, xloc=0.5,
                       yloc=-0.1, ha='center', **kwargs):

        self.stats = {
            'stats': stats_dict,
            'xloc': xloc,
            'yloc': yloc,
            'ha': ha,
            'kwargs': kwargs
        }

    def add_text(self, xloc, yloc, text, transform='datacoords',
                 **kwargs):

        if not hasattr(self, 'text'):
            self.text = []

        self.text.append({
            'xloc': xloc,
            'yloc': yloc,
            'text': text,
            'transform': transform,
            'kwargs': kwargs
        })

class CreateFigure:

    def __init__(self, nrows=1, ncols=1, figsize=(8, 6)):
        self.nrows = nrows
        self.ncols = ncols
        self.figsize = figsize
        self.plot_list = []
        self.fig = None

    def create_figure(self):
        self.fig = self.plot_list[0].plot_layers[0]  
        print(type(self.fig))


    def add_suptitle(self, text, **kwargs):
        pass

    def save_figure(self, pathfile, **kwargs):
        pathfile_dir = os.path.dirname(pathfile)
        if not os.path.exists(pathfile_dir):
            os.makedirs(pathfile_dir)
        bokeh_fig = hv.render(self.fig, backend='bokeh')
        save(bokeh_fig, pathfile)

    def close_figure(self):
        pass 
