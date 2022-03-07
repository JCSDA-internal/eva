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
from eva.utilities.utils import get_schema
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


            # pass configurations and make graphic
            # -------------------
            #self.make_figure(figure_conf, plots, batch_fig)



#    def make_figure(self, figure_conf, plots, batch_fig=False):
#        figure_layout = figure_conf.get("layout")
#        file_type = figure_conf.get("figure file type", "png")
#

