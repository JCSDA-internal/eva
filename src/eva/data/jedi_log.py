# (C) Copyright 2021-2023 NOAA/NWS/EMC
#
# (C) Copyright 2021-2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import numpy as np
import xarray as xr

from eva.eva_base import EvaBase


# --------------------------------------------------------------------------------------------------


# Parameters
space = ' '


# --------------------------------------------------------------------------------------------------


def get_data_from_line(jedi_log_line, search_term, separator, position):

    if search_term in jedi_log_line:
        return jedi_log_line.split(separator)[position]


# --------------------------------------------------------------------------------------------------


def get_from_log(jedi_log_lines, search_term, separator, position):

    # Loop over elements of string
    for jedi_log_line in jedi_log_lines:
        data_val = get_data_from_line(jedi_log_line, search_term, separator, position)
        if data_val is not None:
            return data_val


# --------------------------------------------------------------------------------------------------


def parse_convergence(jedi_log_lines):

    # Get the name of the minimizer
    minimizer_algorithm = get_from_log(jedi_log_lines, 'Minimizer algorithm', '=', 1)

    # Names of the variables to be extracted
    var_names = ['alpha', 'beta', 'gradient_reduction', 'norm_reduction']

    # Search criteria for each variable
    search_strings = [minimizer_algorithm + space + 'alpha',
                      minimizer_algorithm + space + 'beta',
                      'Gradient reduction (',
                      'Norm reduction (']

    # Get the total number of inner iterations across all outer iterations
    inner_iterations = []
    for jedi_log_line in jedi_log_lines:
        inner_iterations_outer = get_data_from_line(jedi_log_line, 'max iter =', space, 4)
        if inner_iterations_outer is not None:
            inner_iterations_outer = inner_iterations_outer.split(',')[0]
            inner_iterations.append(int(inner_iterations_outer))
    total_iterations = sum(inner_iterations)

    # Create a dataset to hold the convergence data
    convergence_ds = xr.Dataset()

    # Add inner and outer loop arrays
    convergence_ds['convergence::inner_loop'] = xr.DataArray(np.zeros(total_iterations, dtype='int32'))
    convergence_ds['convergence::outer_loop'] = xr.DataArray(np.zeros(total_iterations, dtype='int32'))

    # Add variables to the dataset
    for var_name in var_names:
        convergence_ds['convergence::'+var_name] = xr.DataArray(np.zeros(total_iterations,
                                                                      dtype='float32'))

    # Parse all the variables
    outer_loop = 0
    outer_loop_total = 0
    for jedi_log_line in jedi_log_lines:

        # Tick the outer loop
        if 'Configuration for outer iteration' in jedi_log_line:
            outer_loop = outer_loop + 1

        # Tick the inner loop and total inner loop
        inner_loop_this_outer = get_data_from_line(jedi_log_line,
                                                   minimizer_algorithm + space + 'Starting Iteration',
                                                   space, 3)

        if inner_loop_this_outer is not None:
            outer_loop_total = outer_loop_total + 1
            # Add inner loop number to Dataset
            convergence_ds['convergence::inner_loop'].data[outer_loop_total-1] = inner_loop_this_outer
            convergence_ds['convergence::outer_loop'].data[outer_loop_total-1] = outer_loop

        # Extract other things
        for ind, var_name in enumerate(var_names):
            data_found = get_data_from_line(jedi_log_line, search_strings[ind], '=', -1)
            if data_found is not None:
                convergence_ds['convergence::'+var_name].data[outer_loop_total-1] = data_found

    return convergence_ds


# --------------------------------------------------------------------------------------------------


class JediLog(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, data_collections, timing):

        # Get name of the log file to parse
        jedi_log_to_parse = self.config.get('jedi_log_to_parse')

        # Collection name to use
        collection_name = self.config.get('collection_name')

        # Read log file into a list of srings
        with open(jedi_log_to_parse) as jedi_log_to_parse_open:
            jedi_log_lines = jedi_log_to_parse_open.read().split('\n')

        # Get list of things to parse from the dictionary
        data_to_parse = self.config.get('data_to_parse')

        # Loop and add to dataset
        for metric in data_to_parse:
            if metric == 'convergence' and data_to_parse[metric]:
                convergence_ds = parse_convergence(jedi_log_lines)
                # Add to the Eva dataset
                data_collections.create_or_add_to_collection(collection_name, convergence_ds)

        # Write out all the collections
        data_collections.display_collections()
