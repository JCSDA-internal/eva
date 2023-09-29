from eva.eva_path import return_eva_path
from eva.plotting.batch.hvplot.plot_tools.create_plots import CreatePlot, CreateFigure
import os

class HvplotFigureHandler():

    def __init__(self):
        # Define default paths to modules
        self.BACKEND_NAME = "Hvplot"
        self.MODULE_NAME = "eva.plotting.batch.hvplot.diagnostics."

    def create_plot(self, layer_list, proj, domain):
        return CreatePlot(plot_layers=layer_list, projection=proj, domain=domain)

    def create_figure(self, nrows, ncols, figsize):
        return CreateFigure(nrows=nrows, ncols=ncols, figsize=figsize)
