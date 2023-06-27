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
import pandas as pd
import geopandas as gpd
import numpy as np

from eva.data.data_collections import DataCollections
from eva.utilities.logger import Logger
from eva.utilities.timing import Timing
from eva.data.eva_dataset_base import EvaDatasetFactory
from eva.transforms.arithmetic import arithmetic, generate_arithmetic_config
from eva.transforms.accept_where import accept_where, generate_accept_where_config
# --------------------------------------------------------------------------------------------------


class EvaInteractive():

    def __init__(self):

        self.logger = Logger('EvaInteractive')
        self.timer = Timing()
        self.dc_dict = {}
        self.fn_dict = {}
        self.ch_required_dict = {}
        self.var_cache = []

    # --------------------------------------------------------------------------------------------------

    def load_collection(self, collection_name, filenames , eva_class_name, control_file = None):

        #Handle filenames input
        if isinstance(filenames, str):
            filenames = [filenames]

        creator = EvaDatasetFactory()
        data_collection = DataCollections()
        eva_object = creator.create_eva_object(eva_class_name, 'data', self.logger, self.timer)
        config = eva_object.generate_default_config(filenames, collection_name)
        print(config)
        eva_object.execute(config, data_collection, self.timer)

        self.dc_dict[collection_name] = data_collection
        self.fn_dict[collection_name] = filenames[0]

        #open up file to find channel requirements
        if eva_class_name != 'JediLog':
            ds = nc.Dataset(filenames[0])
            if 'Channel' in ds.dimensions.keys():
                self.ch_required_dict[collection_name] = True
            else:
                self.ch_required_dict[collection_name] = False
        else: 
            self.ch_required_dict[collection_name] = False
        self.ch_required_dict[collection_name] = False

  # --------------------------------------------------------------------------------------------------

    def get_data_collection(self, collection_name):
        if collection_name in self.dc_dict.keys():
            return self.dc_dict[collection_name]
        else:
            self.logger.abort(f'Collection name \'{collection_name}\' does not exist. ')

  # --------------------------------------------------------------------------------------------------

    def print_data_collection(self, collection_name):
        if collection_name in self.dc_dict.keys():
            self.dc_dict[collection_name].display_collections()
        else:
            self.logger.abort(f'Collection name \'{collection_name}\' does not exist. ')

  # --------------------------------------------------------------------------------------------------

    def retrieve_var_list(self, collection, group):
        ds = nc.Dataset(self.fn_dict[collection])
        if group in list(ds.groups):
            var_list = list(ds[group].variables)
            self.var_cache = var_list
        return self.var_cache

  # --------------------------------------------------------------------------------------------------

    def arithmetic(self, new_name, expression, collection, var_list=[]):
        # Ensure var_list is not empty
        if not var_list:
           group = re.split(r'\(|\)|-|\*|\+|\/', expression)[0]
           var_list = self.retrieve_var_list(collection, group)

        # Generate default config for transform
        arithmetic_config = generate_arithmetic_config(new_name, expression, collection, var_list)

        # Execute transform
        arithmetic(arithmetic_config, self.dc_dict[collection])
        self.logger.info(f'Added \'{new_name}\' to data collection \'{collection}\'.')

  # --------------------------------------------------------------------------------------------------

    def accept_where(self, new_name, starting_field, where, collection, var_list=[]):
        # Make sure all expressions are in correct format
        for expression in where:
            try:
                group, _, _ = expression.split(' ')
            except Exception:
                self.logger.abort(f'Failed to split \'{expression}\'. Check that ' +
                                    'it has the correct format')
        
        # Set var_list if empty
        if not var_list:
            var_list = self.retrieve_var_list(collection, group)
            
        # Generate default config for transform
        accept_where_config = generate_accept_where_config(new_name, starting_field, 
                                                           where, collection, var_list)

        # Execute transform
        accept_where(accept_where_config, self.dc_dict[collection])
        self.logger.info(f'Added \'{new_name}\' to data collection \'{collection}\'.')

  # --------------------------------------------------------------------------------------------------

    def print_statistics(self, df):
        # for each column, print statistics
        nobs = str(len(df))
        for column in df:
            col = df[column]
            print("name: " + column + 
                  "\n\t minimum: " + str(col.min()) +
                  "\n\t maximum:  " + str(col.max()) + 
                  "\n\t std:  " + str(col.std()))
                  #"\n\t number: " + nobs)

  # --------------------------------------------------------------------------------------------------

    def map_gridded():
        print('map gridded')

    def line_plot():
        print('line plot')

    def histogram():
        print('histogram')

  # --------------------------------------------------------------------------------------------------

    def map_scatter(self, plot_entry):
        #retrieve latitude, longitude, and variable
        df = pd.DataFrame()
        collection, group, variable = plot_entry.split('::')
        df['Latitude'] = self.dc_dict[collection].get_variable_data(collection,
                                                                    'MetaData',
                                                                    'latitude')        
        df['Longitude'] = self.dc_dict[collection].get_variable_data(collection,
                                                                     'MetaData',
                                                                     'longitude')
        df[variable] = self.dc_dict[collection].get_variable_data(collection,
                                                                  group,
                                                                  variable)
        df = df.dropna() 
        gdf = gpd.GeoDataFrame(
            df[variable], geometry=gpd.points_from_xy(x=df.Longitude, y=df.Latitude)
        )
        return gdf.hvplot(global_extent=True, 
                          geo=True, tiles='OSM', 
                          hover_cols=variable, frame_width=700)

  # --------------------------------------------------------------------------------------------------

    def density_plot(self, plot_list, print_stats=True):

        #Make empty dataframe
        df = pd.DataFrame()
        for item in plot_list:
            item_list = item.split('::')
            if len(item_list) == 3:
                collection = item_list[0]
                group = item_list[1]
                variable = item_list[2]

                if self.ch_required_dict[collection] == True:
                    self.logger.abort(f'Please include channel number for \'{item}\'.')

                arr = self.dc_dict[collection].get_variable_data(collection,
                                                                 group,
                                                                 variable)
            elif len(item_list) == 4:
                collection = item_list[0]
                group = item_list[1]
                variable = item_list[2]
                channel = int(item_list[3])
                arr = self.dc_dict[collection].get_variable_data(collection,
                                                                 group,  
                                                                 variable,
                                                                 channel)   
            else:
                self.logger.abort(f'Insufficient info in \'{item}\'.')

            df[item] = arr
            print(np.count_nonzero(~np.isnan(arr)))
             
        if print_stats:
            self.print_statistics(df)
        df = df.dropna() 
        
        return df.hvplot.kde(filled=True, legend='top_left', alpha=0.5, bandwidth=0.1, height=400)               
 
   # --------------------------------------------------------------------------------------------------

    def scatter(self, x, y, print_stats=True):
        df = pd.DataFrame()
        plot_list = [x, y]
        for item in plot_list:
            #split would break here if no channel and channel required, use try/except
            #block and no need to check for channel required
            item_list = item.split('::')
            print(item_list)
            print(len(item_list))
            if len(item_list) == 3:
                collection = item_list[0]
                group = item_list[1]
                variable = item_list[2]

                if self.ch_required_dict[collection] == True:
                    self.logger.abort(f'Please include channel number for \'{item}\'.')

                arr = self.dc_dict[collection].get_variable_data(collection,
                                                                 group,
                                                                 variable)
            elif len(item_list) == 4:
                collection = item_list[0]
                group = item_list[1]
                variable = item_list[2]
                channel = int(item_list[3])
                arr = self.dc_dict[collection].get_variable_data(collection,
                                                                 group,
                                                                 variable,
                                                                 channel)
            else:
                self.logger.abort(f'Insufficient info in \'{item}\'.')
            df[item] = arr

        df = df.dropna()
        if print_stats:
            self.print_statistics(df)

        return df.hvplot.scatter(x, y, s=20, c='b', height=400, width=400)

  # --------------------------------------------------------------------------------------------------
