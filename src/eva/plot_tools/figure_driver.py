# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from eva.eva_base import EvaBase
from eva.eva_path import return_eva_path
from eva.utilities.utils import get_schema, camelcase_to_underscore
from eva.plot_tools.figure import CreatePlot, CreateFigure
import importlib
import os

# --------------------------------------------------------------------------------------------------


class FigureDriver(EvaBase):

    def execute(self, dataobj):

        # Make copy of config
        # -------------------
        config = self.config

        # Get list of graphics from configuration
        # -------------------
        graphics = config.get("graphics")

        # Loop through specified graphics
        # -------------------
        for graphic in graphics:

            # Parse configuration for this graphic
            # -------------------

            # batch_fig = True, loop through all data
            # batch_fig = False, user must specify each plot/panel
            batch_fig = graphic.get("batch figure", False)

            # figure configuration
            figure_conf = graphic.get("figure")

            # update figure conf based on schema
            fig_schema = figure_conf.get("schema",
                                         os.path.join(return_eva_path(),
                                                      'defaults',
                                                      'figure.yaml'))
            figure_conf = get_schema(fig_schema, figure_conf, self.logger)

            # list of plots/subplots
            plots = graphic.get("plots")

            # pass configurations and make graphic(s)
            # -------------------
            if batch_fig:
                # make batch figures for each variable
                print('Nothing for now on batch_fig=True')
            else:
                # make just one figure per configuration
                self.make_figure(figure_conf, plots, dataobj)

    def make_figure(self, figure_conf, plots, dataobj):

        # Grab some figure configuration
        # -------------------
        figure_layout = figure_conf.get("layout")
        file_type = figure_conf.get("figure file type", "png")
        output_file = self.get_output_file(figure_conf)

        # Set up layers and plots
        plot_list = []
        for plot in plots:
            layer_list = []
            for layer in plot.get("layers"):
                eva_class_name = layer.get("type")
                eva_module_name = camelcase_to_underscore(eva_class_name)
                full_module = "eva.diagnostics."+eva_module_name
                layer_class = getattr(importlib.import_module(full_module), eva_class_name)
                # use the translator class to go from eva to declarative plotting
                layer_list.append(layer_class(layer, dataobj).plotobj)
            # create a subplot based on specified layers
            plotobj = CreatePlot(plot_layers=layer_list)
            # make changes to subplot based on YAML configuration
            for key, value in plot.items():
                if key not in ['layers']:
                    if isinstance(value, dict):
                        getattr(plotobj, key)(**value)
                    elif value is None:
                        getattr(plotobj, key)()
                    else:
                        getattr(plotobj, key)(value)
            plot_list.append(plotobj)
        # create figure
        fig = CreateFigure(nrows=figure_conf['layout'][0],
                           ncols=figure_conf['layout'][1],
                           figsize=tuple(figure_conf['figure size']))
        fig.plot_list = plot_list
        fig.create_figure()
        if 'title' in figure_conf:
            fig.add_suptitle(figure_conf['title'])
        saveargs = self.get_saveargs(figure_conf)
        fig.save_figure(output_file, **saveargs)

    def get_saveargs(self, figure_conf):
        out_conf = figure_conf
        delvars = ['layout', 'figure file type', 'output path', 'figure size', 'title']
        out_conf['format'] = figure_conf['figure file type']
        for d in delvars:
            del out_conf[d]
        return out_conf

    def get_output_file(self, figure_conf):
        file_type = figure_conf.get("figure file type", "png")
        file_path = figure_conf.get("output path", "./")
        output_name = figure_conf.get("output name", "")
        output_file = os.path.join(file_path, f"{output_name}.{file_type}")
        return output_file
