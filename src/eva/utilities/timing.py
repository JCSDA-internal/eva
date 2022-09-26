#!/usr/bin/env python

# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import textwrap
import time

from eva.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


class Timing():

    def __init__(self):

        # Logger
        self.logger = Logger('Timers')

        # Record start time for the class
        self.start_time = time.perf_counter()

        # Dictionary to hold timers
        self.timing_dict = {}

    # ----------------------------------------------------------------------------------------------

    def start(self, timer_name):

        # Create this timer and set count to zero
        if timer_name not in self.timing_dict.keys():
            self.timing_dict[timer_name] = {}
            self.timing_dict[timer_name]['count'] = 0
            self.timing_dict[timer_name]['total_time'] = 0.0

        # Check that timer is not already running
        if 'running' in self.timing_dict[timer_name].keys():
            if self.timing_dict[timer_name]['running']:
                self.logger.abort(f'Trying to start the timer for \'{timer_name}\' but it is ' +
                                  f'already running')

        # Record current start time
        self.timing_dict[timer_name]['start_time'] = time.perf_counter()

        # Set that this timer is running
        self.timing_dict[timer_name]['running'] = True

        # Up the count
        self.timing_dict[timer_name]['count'] = self.timing_dict[timer_name]['count'] + 1

    # ----------------------------------------------------------------------------------------------

    def stop(self, timer_name):

        # Check that this timer was initialized
        if timer_name not in self.timing_dict.keys():
            self.logger.abort(f'Trying to stop the timer for {timer_name} but it was never ' +
                              f'initialized.')

        # Check that the timer is in fact running
        if not self.timing_dict[timer_name]['running']:
            self.logger.abort(f'Trying to stop the timer for \'{timer_name}\' but it is not ' +
                              f'running')

        # Record the final time
        elapsed = time.perf_counter() - self.timing_dict[timer_name]['start_time']
        self.timing_dict[timer_name]['total_time'] = self.timing_dict[timer_name]['total_time'] + \
            elapsed

        # Set running back to false
        self.timing_dict[timer_name]['running'] = False

        return

    # ----------------------------------------------------------------------------------------------

    def finalize(self):

        import time

        # Maximum length of a line with timer name
        max_len = 35

        # Total time
        total_time = time.perf_counter() - self.start_time
        total_time_formatted = '{:.2f}'.format(total_time)

        # Log the times
        first = True
        for key in self.timing_dict.keys():

            # Check that no timer is still running
            if self.timing_dict[key]['running']:
                self.logger.abort('Timer \'{key}\' is still running. Make sure it was stopped.')

            name = key

            name_list = textwrap.wrap(key, max_len, break_long_words=True)
            for i in range(0, len(name_list)-1):
                name_list[i] = name_list[i] + ' ...'

            time = self.timing_dict[key]['total_time']
            count = self.timing_dict[key]['count']
            time_per_count = time / count
            time_percent = 100.0 * time / total_time

            name_formatted = name_list[0].ljust(max_len+6)
            time_formatted = '{:8.2f}'.format(time)
            count_formatted = f'{count:03}'
            time_per_count_formatted = '{:8.2f}'.format(time_per_count)
            time_percent_formatted = '{:4.1f}'.format(time_percent)

            write_string = f'{name_formatted} {time_formatted} seconds | ' + \
                           f'Instances count: {count_formatted} | ' + \
                           f'Per instance: {time_per_count_formatted} | ' + \
                           f'Percent of total: {time_percent_formatted}%'

            if first:
                write_str_len = len(write_string)
                self.logger.info(' ')
                self.logger.info('-' * write_str_len)
                self.logger.info(' ')
                self.logger.info('TIMING INFORMATION (seconds)'.center(write_str_len))
                self.logger.info('----------------------------'.center(write_str_len))
                self.logger.info(' ')
                first = False

            # Write timer info
            self.logger.info(write_string)

            for i in range(1, len(name_list)):
                self.logger.info('  ' + name_list[i].ljust(max_len+4))

        self.logger.info(' ')
        self.logger.info(f'Total time taken {total_time_formatted} seconds.')
        self.logger.info(' ')
        self.logger.info('-' * write_str_len)
        self.logger.info(' ')


# --------------------------------------------------------------------------------------------------
