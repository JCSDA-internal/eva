# This work developed by NOAA/NWS/EMC under the Apache 2.0 license.
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.interpolate import interpn
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from eva.plot_tools.maps import Domain, MapProjection
from eva.utilities.stats import get_linear_regression

__all__ = ['CreateFigure', 'CreatePlot']


class CreateFigure:

    def __init__(self, nrows=1, ncols=1, figsize=(8, 6),
                 sharex=False, sharey=False):

        self.nrows = nrows
        self.ncols = ncols
        self.figsize = figsize
        self.sharex = sharex
        self.sharey = sharey
        self.plot_list = []

    def save_figure(self, pathfile, **kwargs):
        """
        Method to save figure to file
        """
        # Create directory if needed
        path, file = os.path.split(pathfile)
        if path != '':
            os.makedirs(path, exist_ok=True)

        # Remove deprecated options from dictionary
        if 'output name' in kwargs:
            del kwargs['output name']

        if 'tight_layout' in kwargs:
            del kwargs['tight_layout']

        # Save figure
        self.fig.savefig(pathfile, **kwargs)

    def close_figure(self):
        """
        Method to close figure
        """
        # Close figure
        plt.close()

    def create_figure(self):
        """
        Driver method to create figure and subplots.
        """

        # Check to make sure plot_list == nrows*ncols
        if len(self.plot_list) != self.nrows*self.ncols:
            raise ValueError(
                'Number of plots does not match the number inputted rows'
                'and columns.')

        plot_dict = {
            'scatter': self._scatter,
            'histogram': self._histogram,
            'density': self._density,
            'line_plot': self._lineplot,
            'vertical_line': self._verticalline,
            'horizontal_line': self._horizontalline,
            'bar_plot': self._barplot,
            'horizontal_bar': self._hbar,
            'map_scatter': self._map_scatter,
            'map_gridded': self._map_gridded,
            'map_contour': self._map_contour
        }

        gs = gridspec.GridSpec(self.nrows, self.ncols)
        self.fig = plt.figure(figsize=self.figsize)

        for i, plot_obj in enumerate(self.plot_list):

            # check if object has projection and domain attributes to determine ax
            if hasattr(plot_obj, 'projection'):
                self.domain = Domain(plot_obj.domain)
                self.projection = MapProjection(plot_obj.projection)

                # Set up axis specific things
                ax = plt.subplot(gs[i], projection=self.projection.projection)
                if str(self.projection) not in ['npstere', 'spstere']:
                    ax.set_extent(self.domain.extent)
                    if str(self.projection) not in ['lamconf']:
                        ax.set_xticks(self.domain.xticks, crs=ccrs.PlateCarree())
                        ax.set_yticks(self.domain.yticks, crs=ccrs.PlateCarree())
                        lon_formatter = LongitudeFormatter(zero_direction_label=False)
                        lat_formatter = LatitudeFormatter()
                        ax.xaxis.set_major_formatter(lon_formatter)
                        ax.yaxis.set_major_formatter(lat_formatter)

            else:
                ax = plt.subplot(gs[i])

            # Loop through plot layers
            for layer in plot_obj.plot_layers:
                plot_dict[layer.plottype](layer, ax)

            # loop through all keys in an object and then call approriate
            # method to plot the feature on the axis
            for feat in vars(plot_obj).keys():
                self._plot_features(plot_obj, feat, ax)

            if self.sharex:
                self._sharex(ax)
            if self.sharey:
                self._sharey(ax)

    def add_suptitle(self, text, **kwargs):
        """
        Add super title to figure. Useful for subplots.
        """
        if hasattr(self, 'fig'):
            self.fig.suptitle(text, **kwargs)

    def _plot_features(self, plot_obj, feature, ax):

        feature_dict = {
            'title': self._plot_title,
            'xlabel': self._plot_xlabel,
            'ylabel': self._plot_ylabel,
            'colorbar': self._plot_colorbar,
            'stats': self._plot_stats,
            'legend': self._plot_legend,
            'text': self._plot_text,
            'grid': self._plot_grid,
            'xlim': self._set_xlim,
            'ylim': self._set_ylim,
            'xticks': self._set_xticks,
            'yticks': self._set_yticks,
            'xticklabels': self._set_xticklabels,
            'yticklabels': self._set_yticklabels,
            'invert_xaxis': self._invert_xaxis,
            'invert_yaxis': self._invert_yaxis,
            'yscale': self._set_yscale,
            'xscale': self._set_xscale,
            'map_features': self._add_map_features
        }

        if feature in feature_dict:
            feature_dict[feature](ax, vars(plot_obj)[feature])

    def _map_scatter(self, plotobj, ax):

        # Flag set for integer fields
        integer_field = False
        if 'integer_field' in vars(plotobj):
            integer_field = True

        if plotobj.data is None:
            skipvars = ['plottype', 'longitude', 'latitude',
                        'markersize', 'integer_field']
            inputs = self._get_inputs_dict(skipvars, plotobj)

            cs = ax.scatter(plotobj.longitude, plotobj.latitude,
                            s=plotobj.markersize, **inputs,
                            transform=self.projection.transform)
        else:
            skipvars = ['plottype', 'longitude', 'latitude',
                        'data', 'markersize', 'colorbar', 'normalize', 'integer_field']
            inputs = self._get_inputs_dict(skipvars, plotobj)

            norm = None
            if integer_field:
                cmap = matplotlib.cm.get_cmap(inputs['cmap'])
                vmin = inputs['vmin']
                vmax = inputs['vmax']
                if vmin is None or vmax is None:
                    print("Abort: vmin and vmax must be set for integer fields")
                    exit()
                norm = matplotlib.colors.BoundaryNorm(np.arange(vmin-0.5, vmax, 1), cmap.N)
            cs = ax.scatter(plotobj.longitude, plotobj.latitude,
                            c=plotobj.data, s=plotobj.markersize,
                            **inputs, norm=norm,
                            transform=self.projection.transform)
        if plotobj.colorbar:
            self.cs = cs

    def _map_gridded(self, plotobj, ax):

        skipvars = ['plottype', 'longitude', 'latitude',
                    'markersize']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        cs = ax.pcolormesh(plotobj.latitude, plotobj.longitude,
                           plotobj.data, **inputs,
                           transform=self.projection.transform)

        if plotobj.colorbar:
            self.cs = cs

    def _map_contour(self, plotobj, ax):

        skipvars = ['plottype', 'longitude', 'latitude',
                    'markersize']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        cs = ax.contour(plotobj.longitude, plotobj.latitude,
                        plot.data, **inputs,
                        transform=self.projection.transform)

        if plotobj.clabel:
            plt.clabel(cs, levels=plotobj.levels, use_clabeltext=True)

        if plotobj.colorbar:
            self.cs = cs

    def _density_scatter(self, plotobj, ax):
        """
        Uses Scatter Object to plot density scatter colored by
        2d histogram.
        """
        _idx = np.logical_and(~np.isnan(plotobj.x), ~np.isnan(plotobj.y))
        data, x_e, y_e = np.histogram2d(plotobj.x[_idx], plotobj.y[_idx],
                                        bins=plotobj.density['bins'],
                                        density=not plotobj.density['nsamples'])
        if plotobj.density['nsamples']:
            # compute percentage of total for each bin
            data = data / np.count_nonzero(_idx) * 100.
        z = interpn((0.5*(x_e[1:] + x_e[:-1]), 0.5*(y_e[1:]+y_e[:-1])),
                    data, np.vstack([plotobj.x, plotobj.y]).T,
                    method=plotobj.density['interp'], bounds_error=False)
        # To be sure to plot all data
        z[np.where(np.isnan(z))] = 0.0
        # Sort the points by density, so that the densest
        # points are plotted last
        if plotobj.density['sort']:
            idx = z.argsort()
            x, y, z = plotobj.x[idx], plotobj.y[idx], z[idx]
        cs = ax.scatter(x, y, c=z,
                        s=plotobj.markersize,
                        cmap=plotobj.density['cmap'],
                        label=plotobj.label)
        # below doing nothing? fix/remove in subsequent PR?
        # norm = Normalize(vmin=np.min(z), vmax=np.max(z))

        if plotobj.density['colorbar']:
            self.cs = cs

    def _scatter(self, plotobj, ax):
        """
        Uses Scatter object to plot on axis.
        """
        # checks to see if density attribute is True
        if hasattr(plotobj, 'density'):
            self._density_scatter(plotobj, ax)
        else:
            skipvars = ['plottype', 'plot_ax', 'x', 'y',
                        'markersize', 'do_linear_regression', 'linear_regression',
                        'density', 'channel']
            inputs = self._get_inputs_dict(skipvars, plotobj)
            s = ax.scatter(plotobj.x, plotobj.y, s=plotobj.markersize,
                           **inputs)

        # checks to see if linear regression attribute
        if plotobj.do_linear_regression:

            # Assert that plotobj contains nonzero-length data
            if len(plotobj.x) != 0 and len(plotobj.y) != 0:
                y_pred, r_sq, intercept, slope = get_linear_regression(plotobj.x,
                                                                       plotobj.y)
                label = f"y = {slope:.4f}x + {intercept:.4f}\nR\u00b2 : {r_sq:.4f}"

                inputs = self._get_inputs_dict([], plotobj)
                if 'color' in plotobj.linear_regression and 'color' in inputs:
                    plotobj.linear_regression['color'] = inputs['color']
                ax.plot(plotobj.x, y_pred, label=label, **plotobj.linear_regression)

    def _lineplot(self, plotobj, ax):
        """
        Uses LinePlot object to plot on axis.
        """
        skipvars = ['plottype', 'plot_ax', 'x', 'y']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        ax.plot(plotobj.x, plotobj.y, **inputs)

    def _histogram(self, plotobj, ax):
        """
        Uses Histogram object to plot on axis.
        """
        skipvars = ['plottype', 'plot_ax', 'data']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        ax.hist(plotobj.data, **inputs)

        # Plot vertical line at x=0
        ax.axvline(x=0, color='k', ls=':', alpha=0.2)

    def _density(self, plotobj, ax):
        """
        Uses Density object to plot on axis.
        """
        import seaborn as sns

        skipvars = ['plottype', 'plot_ax', 'data']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        sns.kdeplot(data=plotobj.data, ax=ax, **inputs)

        # Plot vertical line at x=0
        ax.axvline(x=0, color='k', ls=':', alpha=0.2)

    def _verticalline(self, plotobj, ax):
        """
        Uses VerticalLine object to plot on axis.
        """
        skipvars = ['plottype', 'plot_ax', 'x']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        ax.axvline(plotobj.x, **inputs)

    def _horizontalline(self, plotobj, ax):
        """
        Uses HorizontalLine object to plot on axis.
        """
        skipvars = ['plottype', 'plot_ax', 'y']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        ax.axhline(plotobj.y, **inputs)

    def _barplot(self, plotobj, ax):
        """
        Uses BarPlot object to plot on axis.
        """
        skipvars = ['plottype', 'plot_ax', 'x', 'height']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        ax.bar(plotobj.x, plotobj.height, **inputs)

    def _hbar(self, plotobj, ax):
        """
        Uses HorizontalBar object to plot on axis.
        """
        skipvars = ['plottype', 'plot_ax', 'y', 'width']
        inputs = self._get_inputs_dict(skipvars, plotobj)

        ax.barh(plotobj.y, plotobj.width, **inputs)

    def _get_inputs_dict(self, skipvars, plotobj):
        """
        Creates dictionary for plot inputs. Skips variables
        in 'skipvars' list.
        """
        inputs = {}
        for v in [v for v in vars(plotobj) if v not in skipvars]:
            inputs[v] = vars(plotobj)[v]

        return inputs

    def _plot_title(self, ax, title):
        """
        Add title on specified ax.
        """
        ax.set_title(**title)

    def _plot_xlabel(self, ax, xlabel):
        """
        Add xlabel on specified ax.
        """
        ax.set_xlabel(**xlabel)

    def _plot_ylabel(self, ax, ylabel):
        """
        Add ylabel on specified ax.
        """
        ax.set_ylabel(**ylabel)

    def _plot_colorbar(self, ax, colorbar):
        """
        Add colorbar on specified ax or for total figure.
        """

        if hasattr(self, 'cs'):
            if colorbar['single_cbar']:
                # IMPORTANT NOTICE ####
                # If using single colorbar option, this method grabs the color
                # series from the subplot that is in last row and column. It
                # is important to note that if comparing multiple subplots with
                # the same colorbar, the vmin and vmax should all be the same to
                # avoid comparison errors.
                if ax.is_last_row() and ax.is_last_col():
                    cbar_ax = self.fig.add_axes(colorbar['cbar_loc'])
                    cb = self.fig.colorbar(self.cs, cax=cbar_ax, **colorbar['kwargs'])
                    cb.set_label(colorbar['label'], fontsize=colorbar['fontsize'])

            else:
                cb = self.fig.colorbar(self.cs, ax=ax,
                                       **colorbar['kwargs'])
                cb.set_label(colorbar['label'], fontsize=colorbar['fontsize'])

    def _plot_stats(self, ax, stats):
        """
        Add annotated stats on specified ax.
        """
        # loop through the dictionary and create the sting to annotate
        outstr = ''
        for key, value in stats['stats'].items():
            outstr = outstr + f'{key}: {value}    '

        ax.annotate(outstr, xy=(stats['xloc'], stats['yloc']),
                    xycoords='axes fraction', ha=stats['ha'],
                    **stats['kwargs'])

    def _plot_legend(self, ax, legend):
        """
        Add legend on specified ax.
        """
        leg = ax.legend(**legend)

        for i, key in enumerate(leg.legendHandles):
            leg.legendHandles[i]._sizes = [20]

    def _plot_text(self, ax, text):
        """
        Add text on specified ax.
        """
        ax.text(text['xloc'], text['yloc'],
                text['text'], **text['kwargs'])

    def _plot_grid(self, ax, grid):
        """
        Add grid on specified ax.
        """
        try:
            ax.gridlines(crs=ccrs.PlateCarree(), **grid)
        except AttributeError:
            ax.grid(**grid)

    def _set_xlim(self, ax, xlim):
        """
        Set x-limits on specified ax.
        """
        ax.set_xlim(**xlim)

    def _set_ylim(self, ax, ylim):
        """
        Set y-limits on specified ax.
        """
        ax.set_ylim(**ylim)

    def _set_xticks(self, ax, xticks):
        """
        Set x-ticks on specified ax.
        """
        try:
            ax.set_xticks(**xticks, crs=ccrs.PlateCarree())
            lon_formatter = LongitudeFormatter(zero_direction_label=True)
            lat_formatter = LatitudeFormatter()
            ax.xaxis.set_major_formatter(lon_formatter)
            ax.yaxis.set_major_formatter(lat_formatter)
        except AttributeError:
            ax.set_xticks(**xticks)

    def _set_yticks(self, ax, yticks):
        """
        Set y-ticks on specified ax.
        """
        try:
            ax.set_yticks(**yticks, crs=ccrs.PlateCarree())
        except AttributeError:
            ax.set_yticks(**yticks)

    def _set_xticklabels(self, ax, xticklabels):
        """
        Set x-tick labels on specified ax.
        """
        if len(xticklabels['labels']) == len(ax.get_xticks()):
            ax.set_xticklabels(xticklabels['labels'],
                               **xticklabels['kwargs'])

        else:
            raise ValueError('Len of xtick labels does not equal ' +
                             'len of xticks. Set xticks appropriately ' +
                             'or change labels to be len of xticks.')

    def _set_yticklabels(self, ax, yticklabels):
        """
        Set y-tick labels on specified ax.
        """
        if len(yticklabels['labels']) == len(ax.get_yticks()):
            ax.set_yticklabels(yticklabels['labels'],
                               **yticklabels['kwargs'])

        else:
            raise ValueError('Len of ytick labels does not equal ' +
                             'len of yticks. Set yticks appropriately ' +
                             'or change labels to be len of yticks.')

    def _invert_xaxis(self, ax, invert_xaxis):
        """
        Invert x-axis on specified ax.
        """
        if invert_xaxis:
            ax.invert_xaxis()

    def _invert_yaxis(self, ax, invert_yaxis):
        """
        Invert y-axis on specified ax.
        """
        if invert_yaxis:
            ax.invert_yaxis()

    def _set_xscale(self, ax, xscale):
        """
        Set x-scale on specified ax.
        """
        ax.set_xscale(xscale)

    def _set_yscale(self, ax, yscale):
        """
        Set y-scale on specified ax.
        """
        ax.set_yscale(yscale)

    def _sharex(self, ax):
        """
        If sharex axis is True, will find where to hide xticklabels.
        """
        if not ax.is_last_row():
            plt.setp(ax.get_xticklabels(), visible=False)

    def _sharey(self, ax):
        """
        If sharey axis is True, will find where to hide yticklabels.
        """
        if not ax.is_first_col():
            plt.setp(ax.get_yticklabels(), visible=False)

    def _add_map_features(self, ax, map_features):
        """
        Factory to add map features.
        """
        feature_dict = {
            'coastline': cfeature.COASTLINE,
            'borders': cfeature.BORDERS,
            'states': cfeature.STATES,
            'lakes': cfeature.LAKES,
            'rivers': cfeature.RIVERS,
            'land': cfeature.LAND,
            'ocean': cfeature.OCEAN
        }

        for feat in map_features:
            try:
                ax.add_feature(feature_dict[feat])
            except KeyError:
                raise TypeError(f'{feat} is not a valid map feature.' +
                                'Current map features supported are:\n' +
                                f'{" | ".join(feature_dict.keys())}"')


class CreatePlot():
    """
    Creates a figure to plot data as a scatter plot,
    histogram, density or line plot.
    """
    def __init__(self, plot_layers=[], projection=None,
                 domain=None):

        self.plot_layers = plot_layers

        ###############################################
        # Need a better way of doing this
        if projection is not None and domain is not None:
            self.projection = projection
            self.domain = domain
        ###############################################

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

    def add_legend(self, **kwargs):

        self.legend = {
            **kwargs
        }

    def add_text(self, xloc, yloc, text, **kwargs):

        self.text = {
            'xloc': xloc,
            'yloc': yloc,
            'text': text,
            'kwargs': kwargs
        }

    def add_grid(self, **kwargs):

        self.grid = {
            **kwargs
        }

    def add_map_features(self, feature_list=['coastline']):

        self.map_features = feature_list

    def set_xlim(self, left=None, right=None):

        self.xlim = {
            'left': left,
            'right': right
        }

    def set_ylim(self, bottom=None, top=None):

        self.ylim = {
            'bottom': bottom,
            'top': top
        }

    def set_xticks(self, ticks=list(), minor=False):

        self.xticks = {
            'ticks': ticks,
            'minor': minor
        }

    def set_yticks(self, ticks=list(), minor=False):

        self.yticks = {
            'ticks': ticks,
            'minor': minor
        }

    def set_xticklabels(self, labels=list(), **kwargs):

        self.xticklabels = {
            'labels': labels,
            'kwargs': kwargs
        }

    def set_yticklabels(self, labels=list(), **kwargs):

        self.yticklabels = {
            'labels': labels,
            'kwargs': kwargs
        }

    def invert_xaxis(self):

        self.invert_xaxis = True

    def invert_yaxis(self):

        self.invert_yaxis = True

    def set_xscale(self, scale):

        valid_scales = ['log', 'linear', 'symlog', 'logit']
        if scale not in valid_scales:
            raise ValueError(f'requested scale {scale} is invalid. Valid '
                             f'choices are: {" | ".join(valid_scales)}')
        self.xscale = scale

    def set_yscale(self, scale):
        valid_scales = ['log', 'linear', 'symlog', 'logit']
        if scale not in valid_scales:
            raise ValueError(f'requested scale {scale} is invalid. Valid '
                             f'choices are: {" | ".join(valid_scales)}')

        self.yscale = scale
