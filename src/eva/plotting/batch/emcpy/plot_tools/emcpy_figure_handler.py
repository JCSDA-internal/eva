from emcpy.plots.create_plots import CreatePlot, CreateFigure
from eva.eva_path import return_eva_path
import os

class EmcpyFigureHandler():

    def __init__(self):
        # Define default paths to modules
        self.BACKEND_NAME = "Emcpy"
        self.MODULE_NAME = "eva.plotting.batch.emcpy.diagnostics."

    def find_schema(self, figure_conf):
        return figure_conf.get('schema', os.path.join(return_eva_path(), 'plotting',
                                                      'emcpy', 'defaults', 'figure.yaml'))

    def create_plot(self, layer_list, proj, domain):
        return CreatePlot(plot_layers=layer_list, projection=proj, domain=domain)
    
    def create_figure(self, nrows, ncols, figsize):
        return CreateFigure(nrows=nrows, ncols=ncols, figsize=figsize)
