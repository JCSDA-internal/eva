#!/usr/bin/env python

# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import netCDF4 as nc
import xarray as xr
import re
import numpy as np

from eva.data.data_collections import DataCollections
from eva.utilities.logger import Logger
from eva.utilities.timing import Timing
from eva.data.eva_dataset_base import EvaDatasetFactory
from eva.transforms.arithmetic import arithmetic, generate_arithmetic_config
from eva.transforms.accept_where import accept_where, generate_accept_where_config

import eva.plotting.interactive.interactive_plot_tools as plot


# --------------------------------------------------------------------------------------------------


class EvaInteractive():

    """
    A class for interactive data manipulation and visualization using the EVA framework.

    This class provides methods to load data collections, perform data transformations, and generate
    various types of plots.

    Attributes:
        logger (Logger): An instance of the Logger class for logging messages.
        timer (Timing): An instance of the Timing class for measuring execution time.
        dc_dict (dict): A dictionary containing data collections indexed by collection names.
        fn_dict (dict): A dictionary containing filenames associated with data collections.
        ch_required_dict (dict): A dictionary indicating whether channel requirements are needed for
        each data collection.
        var_cache (list): A list to cache variable names.
    """

    def __init__(self):

        """
        Initialize the EvaInteractive instance with necessary attributes.
        """

        self.logger = Logger('EvaInteractive')
        self.timer = Timing()
        self.dc_dict = {}
        self.fn_dict = {}
        self.ch_required_dict = {}
        self.var_cache = []

    # ----------------------------------------------------------------------------------------------

    def load_collection(self, collection_name, filenames, eva_class_name, control_file=None):

        """
        Load a data collection into the EvaInteractive instance.

        Args:
            collection_name (str): Name for the loaded data collection.
            filenames (str or list): Filename(s) containing the data.
            eva_class_name (str): Name of the EVA class for creating the data collection.
            control_file (str, optional): Path to the control file for configuring data collection.
            Default is None.
        """

        # Handle filenames input
        if isinstance(filenames, str):
            filenames = [filenames]

        creator = EvaDatasetFactory()
        data_collection = DataCollections()
        eva_object = creator.create_eva_object(eva_class_name, 'data', self.logger, self.timer)

        if control_file:
            config = eva_object.generate_default_config(filenames, collection_name, control_file)
        else:
            config = eva_object.generate_default_config(filenames, collection_name)

        eva_object.execute(config, data_collection, self.timer)

        self.dc_dict[collection_name] = data_collection
        self.fn_dict[collection_name] = filenames[0]

        no_ch_dataspaces = ['JediLog', 'MonDataSpace']
        # Open up file to find channel requirements
        if eva_class_name not in no_ch_dataspaces:
            ds = nc.Dataset(filenames[0])
            if 'Channel' in ds.dimensions.keys():
                self.ch_required_dict[collection_name] = True
            else:
                self.ch_required_dict[collection_name] = False
        else:
            self.ch_required_dict[collection_name] = False

    # ----------------------------------------------------------------------------------------------

    def get_data_collection(self, collection_name):

        """
        Retrieve a data collection by its name.

        Args:
            collection_name (str): Name of the data collection to retrieve.

        Returns:
            DataCollections: The retrieved data collection instance.
        Raises:
            Exception: If the specified collection does not exist.
        """

        if collection_name in self.dc_dict.keys():
            return self.dc_dict[collection_name]
        else:
            self.logger.abort(f'Collection name \'{collection_name}\' does not exist. ')

    # ----------------------------------------------------------------------------------------------

    def print_data_collection(self, collection_name):

        """
        Print the content of a data collection.

        Args:
            collection_name (str): Name of the data collection to print.
        """

        if collection_name in self.dc_dict.keys():
            self.dc_dict[collection_name].display_collections()
        else:
            self.logger.abort(f'Collection name \'{collection_name}\' does not exist. ')

    # ----------------------------------------------------------------------------------------------

    def retrieve_var_list(self, collection, group):

        """
        Retrieve a list of variable names from a data collection's group.

        Args:
            collection (str): Name of the data collection.
            group (str): Name of the group within the data collection.

        Returns:
            list: List of variable names within the specified group.
        """

        ds = nc.Dataset(self.fn_dict[collection])
        if group in list(ds.groups):
            var_list = list(ds[group].variables)
            self.var_cache = var_list
        return self.var_cache

    # ----------------------------------------------------------------------------------------------

    def arithmetic(self, new_name, expression, collection, var_list=[]):

        """
        Apply an arithmetic transformation to the data collection.

        Args:
            new_name (str): Name of the new variable to be created.
            expression (str): Arithmetic expression to be evaluated.
            collection (str): Name of the data collection.
            var_list (list, optional): List of variable names to be used in the expression. Default
            is an empty list.
        """

        # Ensure var_list is not empty
        if not var_list:
            group = re.split(r'\(|\)|-|\*|\+|\/', expression)[0]
            var_list = self.retrieve_var_list(collection, group)

        # Generate default config for transform
        arithmetic_config = generate_arithmetic_config(new_name, expression, collection, var_list)

        # Execute transform
        arithmetic(arithmetic_config, self.dc_dict[collection])
        self.logger.info(f'Added \'{new_name}\' to data collection \'{collection}\'.')

    # ----------------------------------------------------------------------------------------------

    def accept_where(self, new_name, starting_field, where, collection, var_list=[]):

        """
        Apply an 'accept_where' transformation to the data collection based on specified conditions.

        Args:
            new_name (str): Name of the new variable to be created.
            starting_field (str): Field to which the 'where' conditions are applied.
            where (list): List of expressions specifying conditions for accepting data.
            collection (str): Name of the data collection.
            var_list (list, optional): List of variable names to be used in the expressions. Default
            is an empty list.
        """

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

    # ----------------------------------------------------------------------------------------------

    def print_statistics(self, df):

        """
        Print statistics for each column in the given DataFrame.

        Args:
            df (DataFrame): The DataFrame containing data.
        """

        # for each column, print statistics
        nobs = str(len(df))
        for column in df:
            col = df[column]
            print("name: " + column +
                  "\n\t minimum: " + str(col.min()) +
                  "\n\t maximum:  " + str(col.max()) +
                  "\n\t std:  " + str(col.std()))

    # ----------------------------------------------------------------------------------------------

    def map_gridded(self):

        """
        Placeholder method for generating a gridded map plot.
        """

        print('map gridded')

    # ----------------------------------------------------------------------------------------------

    def line_plot(self, plot_list):

        """
        Generate a line plot using specified data collections and variables.

        Args:
            plot_list (list): List of dictionaries specifying the plot configuration.

        Returns:
            holoviews.plotting.ElementPlot: The generated line plot.
        """

        return plot.hvplot_line_plot(self.dc_dict, plot_list, self.ch_required_dict, self.logger)

    # ----------------------------------------------------------------------------------------------

    def histogram(self, plot_list):

        """
        Generate a histogram plot using specified data collections and variables.

        Args:
            plot_list (list): List of dictionaries specifying the plot configuration.

        Returns:
            holoviews.plotting.ElementPlot: The generated histogram plot.
        """

        return plot.hvplot_histogram(self.dc_dict, plot_list, self.ch_required_dict, self.logger)

    # ----------------------------------------------------------------------------------------------

    def map_scatter(self, plot_entry):

        """
        Generate a scatter plot on a map using specified data collection and variables.

        Args:
            plot_entry (dict): Dictionary specifying the plot configuration.

        Returns:
            holoviews.plotting.ElementPlot: The generated scatter plot on a map.
        """

        return plot.hvplot_map_scatter(self.dc_dict, plot_entry, self.logger)

    # ----------------------------------------------------------------------------------------------

    def density_plot(self, plot_list):

        """
        Generate a density plot using specified data collections and variables.

        Args:
            plot_list (list): List of dictionaries specifying the plot configuration.

        Returns:
            holoviews.plotting.ElementPlot: The generated density plot.
        """

        return plot.hvplot_density_plot(self.dc_dict, plot_list, self.ch_required_dict, self.logger)

    # ----------------------------------------------------------------------------------------------

    def scatter(self, x, y):

        """
        Generate a scatter plot using specified data collections, variables, and coordinates.

        Args:
            x (str): Name of the variable for the x-coordinate.
            y (str): Name of the variable for the y-coordinate.

        Returns:
            holoviews.plotting.ElementPlot: The generated scatter plot.
        """

        return plot.hvplot_scatter(self.dc_dict, x, y, self.ch_required_dict, self.logger)

    # ----------------------------------------------------------------------------------------------
