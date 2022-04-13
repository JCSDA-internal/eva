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


class TransformDriver(EvaBase):

    def execute(self, data_collections):

        print('In Transform Driver', self.config)

        exit()
