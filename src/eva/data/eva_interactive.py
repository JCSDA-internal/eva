#!/usr/bin/env python

# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import os
import netCDF4 as nc
import hvplot.pandas
import xarray as xr
import re

from eva.data.data_collections import DataCollections
from eva.utilities.logger import Logger
from eva.utilities.timing import Timing
from eva.eva_base import EvaFactory
from eva.transforms.arithmetic import arithmetic
from eva.transforms.accept_where import accept_where
# --------------------------------------------------------------------------------------------------


class EvaInteractive():

    def __init__(self):
        self.data_collection = DataCollections()
        self.logger = Logger('EvaInteractive')
        self.collection = 'interactive'
        self.timer = Timing()
        self.filename = ''
        self.var_cache = []

    def load_ioda(self, filename):
        self.filename = filename
        eva_dict = {'datasets': [{'filenames': [filename],
                                  'groups': [],
                                  'missing_value_threshold': 1.0e06,
                                  'name': self.collection}]}
        creator = EvaFactory()
        eva_data_object = creator.create_eva_object('IodaObsSpace',
                                                    'data',
                                                    eva_dict,
                                                    self.logger,
                                                    self.timer)
        eva_data_object.execute(self.data_collection, self.timer)

    def scatter(self, x, y):
        x_group, x_var = x.split('::')
        y_group, y_var = y.split('::')
        new_x = self.data_collection.get_variable_data_array(self.collection, x_group, x_var)
        new_y = self.data_collection.get_variable_data_array(self.collection, y_group, y_var)
        da = xr.merge([new_x, new_y])
        df = da.to_dataframe()
        df = df.dropna()
        return df.hvplot.scatter(x=x, y=y, s=20, c='b', height=400, width=400)

    def retrieve_var_list(self, group):
        ds = nc.Dataset(self.filename)
        if group in list(ds.groups):
            var_list = list(ds[group].variables)
            self.var_cache = var_list
        return self.var_cache

    def arithmetic(self, new_name, expression):
        # Update new_name
        updated_name = self.collection + '::' + new_name + '::${variable}'

        # Retrieve variable list and fix expression
        groups = re.split(r'\(|\)|-|\*|\+|\/', expression)
        for group in groups:
            if group == groups[0]:
                var_list = self.retrieve_var_list(group)
            expression = expression.replace(group, self.collection +
                                            '::' + group + '::${variable}')
        # Build dictionary
        arithmetic_config = {
                             'new name': updated_name,
                             'transform': "arithmetic",
                             'for': {
                               'variable': var_list
                              },
                             'equals': expression
                             }

        arithmetic(arithmetic_config, self.data_collection)
        self.logger.info(f'Added \'{new_name}\' to data collection.')

    def accept_where(self, new_name, starting_field, where):
        # Update new_name
        updated_name = self.collection + '::' + new_name + '::${variable}'
        starting_field = self.collection + '::' + starting_field + '::${variable}'

        for index, expression in enumerate(where):
            # Get group
            try:
                group, _, _ = expression.split(' ')
                var_list = self.retrieve_var_list(group)
            except Exception:
                self.logger.abort(f'Failed to split \'{expression}\'. Check that ' +
                                  'it has the correct format')
            where[index] = expression.replace(group, self.collection +
                                              '::' + group + '::${variable}')
        # Build dict
        accept_where_config = {
                                  'new name': updated_name,
                                  'where': where,
                                  'transform': 'accept where',
                                  'starting field': starting_field,
                                  'for': {
                                     "variable": var_list
                                  }
                              }

        accept_where(accept_where_config, self.data_collection)
        self.logger.info(f'Added \'{new_name}\' to data collection.')

    def print_data_collection(self):
        self.data_collection.display_collections()
