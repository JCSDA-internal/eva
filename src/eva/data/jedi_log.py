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
        return  jedi_log_line.split(separator)[position]


# --------------------------------------------------------------------------------------------------


class JediLog(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, data_collections, timing):

        # Get name of the log file to parse
        jedi_log_to_parse = self.config.get('jedi_log_to_parse')

        # Collection name to use
        collection_name = self.config.get('collection_name')

        # Read log file into a string
        with open(jedi_log_to_parse) as jedi_log_to_parse_open:
            self.jedi_log_text = jedi_log_to_parse_open.read()

        # Split log into list of lines
        self.jedi_log_lines = self.jedi_log_text.split('\n')

        # Split log into list of strings. Each element is all lines between two empty lines in the
        # in the log file.
        chunk_start_points = [-1]
        for jedi_log_line_ind, jedi_log_line in enumerate(self.jedi_log_lines):
            if jedi_log_line == '':
                chunk_start_points.append(jedi_log_line_ind)
        chunk_start_points.append(len(self.jedi_log_lines)+1)

        self.log_chunks = []
        for i in range(len(chunk_start_points)-2):
            chunk = self.jedi_log_lines[chunk_start_points[i]+1:chunk_start_points[i+1]]
            self.log_chunks.append('\n'.join(chunk))

        # Get list of things to parse from the dictionary
        data_to_parse = self.config.get('data_to_parse')

        # Loop and add to dataset
        for metric in data_to_parse:
            if metric == 'convergence' and data_to_parse[metric]:
                convergence_ds = self.parse_convergence()
                # Add to the Eva dataset
                data_collections.create_or_add_to_collection(collection_name, convergence_ds)

        # Write out all the collections
        data_collections.display_collections()


    # ----------------------------------------------------------------------------------------------


    def get_from_log(self, search_term, separator, position, custom_log = None):

        # This method will search every line of the log for the search term

        if custom_log is None:
            log = self.jedi_log_lines
        else:
            log = custom_log

        # Loop over elements of string
        for jedi_log_line in log:
            data_val = get_data_from_line(jedi_log_line, search_term, separator, position)
            if data_val is not None:
                return data_val
        return None


    # ----------------------------------------------------------------------------------------------


    def get_matching_chunks(self, search_terms):

        # Create array to hold chunks that match
        matching_chunks = []

        # Loop over elements of string
        for log_chunk in self.log_chunks:

            # Build an array to check each match
            search_terms_match = []
            for search_term in search_terms:
                search_terms_match.append(search_term in log_chunk)

            # Append if all search terms are in the chunk
            if all(search_terms_match):
                matching_chunks.append(log_chunk)

        return matching_chunks



    # ----------------------------------------------------------------------------------------------


    def parse_convergence(self):

        # Get the name of the minimizer
        minimizer_algorithm = self.get_from_log('Minimizer algorithm', '=', 1)

        # Get the chunks for the minimizer part (Norm reduction etc)
        minimizer_chunks_strings = [f'{minimizer_algorithm} Starting Iteration',
                                    f'{minimizer_algorithm} end of iteration']
        minimizer_chunks = self.get_matching_chunks(minimizer_chunks_strings)

        # Get the chunks for the J, Jb, JoJc part
        j_chunks_strings = [f'Quadratic cost function: J ',
                                    f'Quadratic cost function: Jb']
        j_chunks = self.get_matching_chunks(j_chunks_strings)

        # Total number of inner iterations
        total_iter = len(minimizer_chunks)

        # Check that some minimizer chunks were found
        if total_iter == 0:
            self.logger.abort('The number of iterations found in the log is zero. Check the ' +
                              'parsing of the log is correct.')

        # Create list of variables that need to be built
        var_names = []
        var_search_criteria = []
        var_split = []
        var_position = []
        var_dtype = []
        if minimizer_chunks:

            # Inner iteration number
            var_names.append('inner_iteration')
            var_search_criteria.append(f'{minimizer_algorithm} Starting Iteration')
            var_split.append('Iteration')
            var_position.append(1)
            var_dtype.append('int32')

            # Gradient reduction
            var_names.append('gradient_reduction')
            var_search_criteria.append('Gradient reduction (')
            var_split.append('=')
            var_position.append(1)
            var_dtype.append('float32')

            # Norm reduction
            var_names.append('norm_reduction')
            var_search_criteria.append('Norm reduction (')
            var_split.append('=')
            var_position.append(1)
            var_dtype.append('float32')

        if j_chunks:

            # Inner iteration number
            var_names.append('j')
            var_search_criteria.append('Quadratic cost function: J ')
            var_split.append('=')
            var_position.append(1)
            var_dtype.append('float32')

            # Gradient reduction
            var_names.append('jb')
            var_search_criteria.append('Quadratic cost function: Jb')
            var_split.append('=')
            var_position.append(1)
            var_dtype.append('float32')

            # Norm reduction
            var_names.append('jojc')
            var_search_criteria.append('Quadratic cost function: JoJc')
            var_split.append('=')
            var_position.append(1)
            var_dtype.append('float32')


        # Create a dataset to hold the convergence data
        convergence_ds = xr.Dataset()

        # Concatenate chunks to simplify search algorithm
        min_and_j_chunks = minimizer_chunks + j_chunks

        for var_ind, var in enumerate(var_names):
            var_array = []
            for min_and_j_chunk in min_and_j_chunks:
                min_and_j_chunk_split = min_and_j_chunk.split('\n')
                var_found = self.get_from_log(var_search_criteria[var_ind], var_split[var_ind],
                                              var_position[var_ind], min_and_j_chunk_split)
                if var_found:
                    var_array.append(var_found)

            # Add to the dataset if there is something to add
            if var_array:
                gn = f'convergence::{var_names[var_ind]}' # group::variable name
                convergence_ds[gn] = xr.DataArray(np.zeros(total_iter, dtype=var_dtype[var_ind]))
                convergence_ds[gn].data[:] = var_array

        # Create special case variables

        # Outer iteration
        if 'convergence::inner_iteration' in convergence_ds:
            inner_iterations = convergence_ds['convergence::inner_iteration'].data[:]

            for

            print(inner_iterations)

        exit()

        return convergence_ds


    # ----------------------------------------------------------------------------------------------
