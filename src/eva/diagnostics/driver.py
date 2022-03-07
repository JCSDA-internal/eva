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
from eva.utilities.utils import get_schema
from eva import repo_directory
import os

# --------------------------------------------------------------------------------------------------


class DiagnosticDriver(EvaBase):

    def execute(self):

        # Make copy of config
        # -------------------
        config = self.config

        # Get list of diagnostics from configuration
        # -------------------
        diagnostics = config.get("diagnostics")

        # Loop through specified diagnostics
        # -------------------
        for diagnostic in diagnostics:

            # Parse configuration for this diagnostic
            # -------------------

            # batch_fig = True, loop through all data
            # batch_fig = False, user must specify each plot/panel
            batch_fig = diagnostic.get("batch figure", False)

            # figure configuration
            figure_conf = diagnostic.get("figure")

            # update figure conf based on schema
            fig_schema = figure_conf.get("schema",
                                         os.path.join(repo_directory,
                                                      'defaults',
                                                      'figure.yaml'))
            figure_conf = get_schema(fig_schema, figure_conf, self.logger)

            # list of plots/subplots
            plots = diagnostic.get("plots")

            # pass configurations and make diagnostic
            # -------------------
            self.make_figure(figure_conf, plots, batch_fig)



    def make_figure(self, figure_conf, plots, batch_fig=False):


            figure_layout = figure_conf.get("layout")
            file_type = figure_conf.get("figure file type", "png")


